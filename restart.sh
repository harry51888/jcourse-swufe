#!/bin/bash

# JCourse-SWUFE 重启脚本
# 用于重启整个系统服务

echo "🔄 重启 JCourse-SWUFE 系统..."

# 检查当前目录
if [ ! -d "jcourse_api-master" ] || [ ! -d "jcourse-master" ]; then
    echo "❌ 错误：请在 jcourse-swufe 根目录下运行此脚本"
    exit 1
fi

# 停止服务
echo "🛑 停止现有服务..."
./stop.sh

# 等待服务完全停止
echo "⏳ 等待服务完全停止..."
sleep 5

# 启动服务
echo "🚀 启动服务..."
./start.sh

echo ""
echo "🎉 JCourse-SWUFE 系统重启完成！"