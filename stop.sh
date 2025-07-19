#!/bin/bash

# JCourse-SWUFE 停止脚本
# 用于停止整个系统服务

echo "🛑 停止 JCourse-SWUFE 系统..."

# 检查当前目录
if [ ! -d "jcourse_api-master" ] || [ ! -d "jcourse-master" ]; then
    echo "❌ 错误：请在 jcourse-swufe 根目录下运行此脚本"
    exit 1
fi

# 停止前端服务
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "🎨 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo "✅ 前端服务已停止"
    else
        echo "⚠️  前端服务进程不存在"
    fi
    rm -f frontend.pid
else
    echo "⚠️  未找到前端服务PID文件"
fi

# 停止后端服务
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "🔧 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo "✅ 后端服务已停止"
    else
        echo "⚠️  后端服务进程不存在"
    fi
    rm -f backend.pid
else
    echo "⚠️  未找到后端服务PID文件"
fi

# 停止 Next.js dev server (可能以其他方式运行)
echo "🔍 查找并停止其他 Next.js 进程..."
pkill -f "next dev" 2>/dev/null && echo "✅ 停止了额外的 Next.js 进程"

# 停止 Django runserver 进程
echo "🔍 查找并停止其他 Django 进程..."
pkill -f "manage.py runserver" 2>/dev/null && echo "✅ 停止了额外的 Django 进程"

# 停止数据库和Redis服务
echo "📦 停止数据库和Redis服务..."
cd jcourse_api-master
docker-compose -f docker-compose.dev.yml down

cd ..

echo ""
echo "✅ JCourse-SWUFE 系统已完全停止！"
echo ""
echo "💡 使用 ./start.sh 启动服务"
echo "💡 使用 ./status.sh 查看服务状态"