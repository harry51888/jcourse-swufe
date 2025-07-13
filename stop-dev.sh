#!/bin/bash

# JCourse 开发环境停止脚本
# 使用方法: ./stop-dev.sh

echo "🛑 停止 JCourse 开发环境..."

# 停止后端服务
if [ -f "jcourse_api-master/backend.pid" ]; then
    BACKEND_PID=$(cat jcourse_api-master/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🔧 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm jcourse_api-master/backend.pid
    else
        echo "⚠️  后端服务已停止"
        rm -f jcourse_api-master/backend.pid
    fi
else
    echo "⚠️  未找到后端服务PID文件"
fi

# 停止前端服务
if [ -f "jcourse-master/frontend.pid" ]; then
    FRONTEND_PID=$(cat jcourse-master/frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🎨 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm jcourse-master/frontend.pid
    else
        echo "⚠️  前端服务已停止"
        rm -f jcourse-master/frontend.pid
    fi
else
    echo "⚠️  未找到前端服务PID文件"
fi

# 停止数据库服务
echo "📦 停止数据库服务..."
cd jcourse_api-master
docker-compose -f docker-compose.dev.yml down

echo "✅ 所有服务已停止"
echo ""
echo "💡 提示:"
echo "  - 数据库数据已保存在Docker卷中"
echo "  - 使用 ./start-dev.sh 可以重新启动所有服务"
echo "  - 如需完全清理数据库: docker-compose -f docker-compose.dev.yml down -v"
