#!/bin/bash

# JCourse 开发环境快速启动脚本
# 使用方法: ./start-dev.sh

echo "🚀 启动 JCourse 开发环境..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker Desktop"
    exit 1
fi

# 启动数据库服务
echo "📦 启动数据库服务..."
cd jcourse_api-master
docker-compose -f docker-compose.dev.yml up -d

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 5

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 检查数据库连接
echo "🔍 检查数据库连接..."
if ! DJANGO_SETTINGS_MODULE=jcourse.settings python3 -c "
import django
django.setup()
from django.db import connection
connection.ensure_connection()
print('数据库连接成功')
" 2>/dev/null; then
    echo "❌ 数据库连接失败，请检查配置"
    exit 1
fi

# 启动后端服务（后台运行）
echo "🔧 启动后端服务..."
nohup python3 manage.py runserver 0.0.0.0:8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务 PID: $BACKEND_PID"

# 等待后端启动
sleep 3

# 启动前端服务（后台运行）
echo "🎨 启动前端服务..."
cd ../jcourse-master
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务 PID: $FRONTEND_PID"

# 等待前端启动
sleep 5

echo "✅ 开发环境启动完成！"
echo ""
echo "📊 服务状态:"
echo "  - 后端API: http://localhost:8000"
echo "  - 前端界面: http://localhost:3000"
echo "  - 数据库: PostgreSQL (Docker)"
echo ""
echo "📝 日志文件:"
echo "  - 后端日志: jcourse_api-master/backend.log"
echo "  - 前端日志: jcourse-master/frontend.log"
echo ""
echo "🛑 停止服务:"
echo "  - 停止后端: kill $BACKEND_PID"
echo "  - 停止前端: kill $FRONTEND_PID"
echo "  - 停止数据库: cd jcourse_api-master && docker-compose -f docker-compose.dev.yml down"
echo ""
echo "🌐 打开浏览器访问: http://localhost:3000"

# 保存PID到文件，方便后续停止
echo $BACKEND_PID > jcourse_api-master/backend.pid
echo $FRONTEND_PID > jcourse-master/frontend.pid

echo ""
echo "💡 提示: 使用 ./stop-dev.sh 可以停止所有服务"
