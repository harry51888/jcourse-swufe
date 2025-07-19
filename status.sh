#!/bin/bash

# JCourse-SWUFE 状态查看脚本
# 用于查看系统服务运行状态

echo "📊 JCourse-SWUFE 系统状态"
echo "================================"

# 检查当前目录
if [ ! -d "jcourse_api-master" ] || [ ! -d "jcourse-master" ]; then
    echo "❌ 错误：请在 jcourse-swufe 根目录下运行此脚本"
    exit 1
fi

# 检查前端服务状态
echo ""
echo "🎨 前端服务状态："
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "  ✅ 运行中 (PID: $FRONTEND_PID)"
        echo "  📍 访问地址: http://localhost:3000"
    else
        echo "  ❌ 未运行 (PID文件存在但进程不存在)"
    fi
else
    echo "  ❌ 未运行 (无PID文件)"
fi

# 检查其他 Next.js 进程
NEXTJS_PROCESSES=$(pgrep -f "next dev" | wc -l)
if [ $NEXTJS_PROCESSES -gt 0 ]; then
    echo "  ℹ️  发现 $NEXTJS_PROCESSES 个 Next.js 进程"
fi

# 检查后端服务状态
echo ""
echo "🔧 后端服务状态："
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "  ✅ 运行中 (PID: $BACKEND_PID)"
        echo "  📍 API地址: http://localhost:8000"
        echo "  📍 管理后台: http://localhost:8000/admin"
    else
        echo "  ❌ 未运行 (PID文件存在但进程不存在)"
    fi
else
    echo "  ❌ 未运行 (无PID文件)"
fi

# 检查其他 Django 进程
DJANGO_PROCESSES=$(pgrep -f "manage.py runserver" | wc -l)
if [ $DJANGO_PROCESSES -gt 0 ]; then
    echo "  ℹ️  发现 $DJANGO_PROCESSES 个 Django 进程"
fi

# 检查数据库和Redis状态
echo ""
echo "📦 数据库和Redis状态："
cd jcourse_api-master

POSTGRES_STATUS=$(docker-compose -f docker-compose.dev.yml ps postgres | grep "Up" | wc -l)
REDIS_STATUS=$(docker-compose -f docker-compose.dev.yml ps redis | grep "Up" | wc -l)

if [ $POSTGRES_STATUS -gt 0 ]; then
    echo "  ✅ PostgreSQL: 运行中"
else
    echo "  ❌ PostgreSQL: 未运行"
fi

if [ $REDIS_STATUS -gt 0 ]; then
    echo "  ✅ Redis: 运行中"
else
    echo "  ❌ Redis: 未运行"
fi

cd ..

# 检查端口占用情况
echo ""
echo "🌐 端口占用情况："
check_port() {
    local port=$1
    local service=$2
    if lsof -i :$port > /dev/null 2>&1; then
        echo "  ✅ 端口 $port ($service): 已占用"
    else
        echo "  ❌ 端口 $port ($service): 未占用"
    fi
}

check_port 3000 "前端"
check_port 8000 "后端"
check_port 5433 "PostgreSQL"
check_port 6379 "Redis"

# 显示最近的日志文件大小
echo ""
echo "📁 日志文件状态："
if [ -f "jcourse_api-master/backend.log" ]; then
    BACKEND_LOG_SIZE=$(du -h jcourse_api-master/backend.log | cut -f1)
    echo "  📝 后端日志: $BACKEND_LOG_SIZE (jcourse_api-master/backend.log)"
else
    echo "  📝 后端日志: 不存在"
fi

if [ -f "jcourse-master/frontend.log" ]; then
    FRONTEND_LOG_SIZE=$(du -h jcourse-master/frontend.log | cut -f1)
    echo "  📝 前端日志: $FRONTEND_LOG_SIZE (jcourse-master/frontend.log)"
else
    echo "  📝 前端日志: 不存在"
fi

# 系统资源使用情况
echo ""
echo "💻 系统资源："
echo "  🖥️  CPU使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')%"
echo "  🧠 内存使用: $(free -h | awk 'NR==2{printf "%.1f%%", $3*100/$2 }')"
echo "  💾 磁盘使用: $(df -h . | awk 'NR==2{print $5}')"

echo ""
echo "💡 管理命令："
echo "  ./start.sh   - 启动服务"
echo "  ./stop.sh    - 停止服务"
echo "  ./restart.sh - 重启服务"