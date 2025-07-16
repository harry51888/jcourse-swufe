#!/bin/bash

# JCourse 完整本地部署脚本
# 包括教师评价数据集成
# 使用方法: ./deploy-local.sh

set -e  # 遇到错误立即退出

echo "🚀 JCourse 完整本地部署开始..."
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 检查环境依赖
check_dependencies() {
    log_info "检查环境依赖..."
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
        log_error "Python 版本需要 3.9+，当前版本: $PYTHON_VERSION"
        exit 1
    fi
    log_success "Python $PYTHON_VERSION ✓"
    
    # 检查 Node.js
    check_command "node"
    NODE_VERSION=$(node --version)
    log_success "Node.js $NODE_VERSION ✓"
    
    # 检查 npm
    check_command "npm"
    NPM_VERSION=$(npm --version)
    log_success "npm $NPM_VERSION ✓"
    
    # 检查 Docker
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker 未运行，请先启动 Docker Desktop"
        exit 1
    fi
    log_success "Docker ✓"
    
    # 检查 pip
    check_command "pip3"
    log_success "pip3 ✓"
}

# 设置后端环境
setup_backend() {
    log_info "设置后端环境..."
    
    cd jcourse_api-master
    
    # 创建虚拟环境（可选）
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    log_info "安装Python依赖..."
    pip3 install -r requirements.txt
    
    # 创建环境变量文件
    if [ ! -f ".env" ]; then
        log_info "创建环境变量文件..."
        cat > .env << EOF
DEBUG=True
POSTGRES_PASSWORD=jcourse
POSTGRES_HOST=localhost
REDIS_HOST=localhost
SECRET_KEY=django-insecure-dev-key-for-local-development-$(date +%s)
HASH_SALT=dev-salt-$(date +%s)
EOF
        log_success "环境变量文件创建完成"
    fi
    
    cd ..
}

# 启动数据库服务
setup_database() {
    log_info "启动数据库服务..."
    
    cd jcourse_api-master
    
    # 检查 docker-compose.dev.yml 是否存在
    if [ ! -f "docker-compose.dev.yml" ]; then
        log_info "创建 docker-compose.dev.yml..."
        cat > docker-compose.dev.yml << EOF
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: jcourse
      POSTGRES_USER: jcourse
      POSTGRES_PASSWORD: jcourse
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    restart: unless-stopped

volumes:
  postgres_data:
EOF
    fi
    
    # 启动数据库
    docker-compose -f docker-compose.dev.yml up -d
    
    # 等待数据库启动
    log_info "等待数据库启动..."
    sleep 10
    
    # 检查数据库连接
    log_info "检查数据库连接..."
    if ! python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jcourse.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
print('数据库连接成功')
" 2>/dev/null; then
        log_error "数据库连接失败"
        exit 1
    fi
    
    log_success "数据库服务启动成功"
    cd ..
}

# 初始化Django数据库
init_django() {
    log_info "初始化Django数据库..."
    
    cd jcourse_api-master
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 数据库迁移
    python3 manage.py migrate
    
    # 创建超级用户（如果不存在）
    if ! python3 manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('超级用户创建成功')
else:
    print('超级用户已存在')
"; then
        log_warning "超级用户创建失败或已存在"
    fi
    
    log_success "Django数据库初始化完成"
    cd ..
}

# 导入课表数据
import_course_data() {
    log_info "导入课表数据..."

    cd jcourse_api-master
    source venv/bin/activate

    # 检查课表数据文件
    COURSE_DATA_DIR="../课表数据"
    if [ ! -d "$COURSE_DATA_DIR" ]; then
        log_warning "课表数据目录不存在，跳过课表数据导入"
        cd ..
        return
    fi

    # 检查导入脚本
    if [ ! -f "scripts/import_course_schedule.py" ]; then
        log_warning "课表导入脚本不存在，跳过课表数据导入"
        cd ..
        return
    fi

    # 导入各学期课表数据
    for csv_file in "$COURSE_DATA_DIR"/*.csv; do
        if [ -f "$csv_file" ]; then
            filename=$(basename "$csv_file")
            semester=$(echo "$filename" | sed 's/课表.*\.csv//' | sed 's/[()].*$//')
            log_info "导入 $filename -> $semester"
            python3 scripts/import_course_schedule.py "$csv_file" "$semester" || log_warning "导入 $filename 失败"
        fi
    done

    log_success "课表数据导入完成"
    cd ..
}

# 导入教师评价数据
import_teacher_evaluations() {
    log_info "导入教师评价数据..."

    cd jcourse_api-master
    source venv/bin/activate

    # 检查教师评价数据文件
    EVALUATION_FILE="../jcourse-data/merged_teacher_evaluations.csv"
    if [ ! -f "$EVALUATION_FILE" ]; then
        log_warning "教师评价数据文件不存在，跳过教师评价数据导入"
        cd ..
        return
    fi

    # 检查导入脚本
    if [ ! -f "scripts/import_teacher_evaluations.py" ]; then
        log_warning "教师评价导入脚本不存在，跳过教师评价数据导入"
        cd ..
        return
    fi

    # 导入教师评价数据
    log_info "导入教师评价数据: $EVALUATION_FILE"
    python3 scripts/import_teacher_evaluations.py "$EVALUATION_FILE" || log_warning "导入教师评价数据失败"

    log_success "教师评价数据导入完成"
    cd ..
}

# 设置前端环境
setup_frontend() {
    log_info "设置前端环境..."
    
    cd jcourse-master
    
    # 安装依赖
    log_info "安装前端依赖..."
    npm install --legacy-peer-deps
    
    # 创建环境变量文件
    if [ ! -f ".env.local" ]; then
        log_info "创建前端环境变量文件..."
        cat > .env.local << EOF
REMOTE_URL=http://localhost:8000
EOF
        log_success "前端环境变量文件创建完成"
    fi
    
    cd ..
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动后端
    cd jcourse_api-master
    source venv/bin/activate
    log_info "启动后端服务..."
    nohup python3 manage.py runserver 0.0.0.0:8000 > backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid
    cd ..
    
    # 等待后端启动
    sleep 5
    
    # 启动前端
    cd jcourse-master
    log_info "启动前端服务..."
    nohup npm run dev > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > frontend.pid
    cd ..
    
    # 等待前端启动
    sleep 8
    
    log_success "服务启动完成"
    
    echo ""
    echo "🎉 JCourse 本地部署完成！"
    echo "=================================="
    echo ""
    echo "📊 服务状态:"
    echo "  - 后端API: http://localhost:8000"
    echo "  - 前端界面: http://localhost:3000"
    echo "  - 管理后台: http://localhost:8000/admin"
    echo "  - 数据库: PostgreSQL (Docker)"
    echo ""
    echo "🔑 管理员账号:"
    echo "  - 用户名: admin"
    echo "  - 密码: admin123"
    echo ""
    echo "📝 日志文件:"
    echo "  - 后端日志: jcourse_api-master/backend.log"
    echo "  - 前端日志: jcourse-master/frontend.log"
    echo ""
    echo "🛑 停止服务:"
    echo "  - 使用脚本: ./stop-dev.sh"
    echo "  - 手动停止: kill $BACKEND_PID $FRONTEND_PID"
    echo ""
    echo "🌐 打开浏览器访问: http://localhost:3000"
}

# 主函数
main() {
    # 检查是否在正确的目录
    if [ ! -d "jcourse-master" ] || [ ! -d "jcourse_api-master" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    check_dependencies
    setup_backend
    setup_database
    init_django
    import_course_data
    import_teacher_evaluations
    setup_frontend
    start_services
}

# 执行主函数
main "$@"
