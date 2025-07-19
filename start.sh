#!/bin/bash

# JCourse-SWUFE 启动脚本
# 用于启动整个系统服务

echo "🚀 启动 JCourse-SWUFE 系统..."

# 检查当前目录
if [ ! -d "jcourse_api-master" ] || [ ! -d "jcourse-master" ]; then
    echo "❌ 错误：请在 jcourse-swufe 根目录下运行此脚本"
    exit 1
fi

# 启动数据库和Redis服务
echo "📦 启动数据库和Redis服务..."
cd jcourse_api-master
docker-compose -f docker-compose.dev.yml up -d

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 10

# 启动后端服务
echo "🔧 启动后端服务..."
source venv/bin/activate
nohup python manage.py runserver 0.0.0.0:8000 --insecure > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 返回根目录启动前端
cd ../jcourse-master

# 检查 Node.js 依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 启动前端服务
echo "🎨 启动前端服务..."
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"

# 返回根目录
cd ..

echo ""
echo "🎉 JCourse-SWUFE 系统启动完成！"
echo ""
echo "📊 服务状态："
echo "  - 前端服务: http://localhost:3000"
echo "  - 后端服务: http://localhost:8000"
echo "  - 管理后台: http://localhost:8000/admin"
echo ""
echo "📝 进程信息："
echo "  - 后端进程 PID: $BACKEND_PID"
echo "  - 前端进程 PID: $FRONTEND_PID"
echo ""
echo "📁 日志文件："
echo "  - 后端日志: jcourse_api-master/backend.log"
echo "  - 前端日志: jcourse-master/frontend.log"
echo ""
echo "💡 使用 ./stop.sh 停止服务"
echo "💡 使用 ./restart.sh 重启服务"
echo "💡 使用 ./status.sh 查看服务状态"