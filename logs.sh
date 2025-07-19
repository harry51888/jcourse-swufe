#!/bin/bash

# JCourse-SWUFE 日志查看脚本
# 用于查看系统日志

echo "📝 JCourse-SWUFE 日志查看"
echo "================================"

# 检查当前目录
if [ ! -d "jcourse_api-master" ] || [ ! -d "jcourse-master" ]; then
    echo "❌ 错误：请在 jcourse-swufe 根目录下运行此脚本"
    exit 1
fi

# 显示菜单
echo ""
echo "请选择要查看的日志："
echo "1) 后端日志 (实时)"
echo "2) 前端日志 (实时)"
echo "3) 后端日志 (最后50行)"
echo "4) 前端日志 (最后50行)"
echo "5) 数据库日志"
echo "6) Redis日志"
echo "7) 系统进程信息"
echo "0) 退出"
echo ""

read -p "请输入选项 (0-7): " choice

case $choice in
    1)
        echo "📊 实时查看后端日志 (按 Ctrl+C 退出)..."
        if [ -f "jcourse_api-master/backend.log" ]; then
            tail -f jcourse_api-master/backend.log
        else
            echo "❌ 后端日志文件不存在"
        fi
        ;;
    2)
        echo "📊 实时查看前端日志 (按 Ctrl+C 退出)..."
        if [ -f "jcourse-master/frontend.log" ]; then
            tail -f jcourse-master/frontend.log
        else
            echo "❌ 前端日志文件不存在"
        fi
        ;;
    3)
        echo "📊 后端日志 (最后50行):"
        if [ -f "jcourse_api-master/backend.log" ]; then
            tail -n 50 jcourse_api-master/backend.log
        else
            echo "❌ 后端日志文件不存在"
        fi
        ;;
    4)
        echo "📊 前端日志 (最后50行):"
        if [ -f "jcourse-master/frontend.log" ]; then
            tail -n 50 jcourse-master/frontend.log
        else
            echo "❌ 前端日志文件不存在"
        fi
        ;;
    5)
        echo "📊 数据库日志:"
        cd jcourse_api-master
        docker-compose -f docker-compose.dev.yml logs postgres
        cd ..
        ;;
    6)
        echo "📊 Redis日志:"
        cd jcourse_api-master
        docker-compose -f docker-compose.dev.yml logs redis
        cd ..
        ;;
    7)
        echo "📊 系统进程信息:"
        echo ""
        echo "JCourse 相关进程:"
        ps aux | grep -E "(next|django|manage.py|runserver)" | grep -v grep
        echo ""
        echo "Docker 容器:"
        cd jcourse_api-master
        docker-compose -f docker-compose.dev.yml ps
        cd ..
        ;;
    0)
        echo "👋 退出日志查看"
        ;;
    *)
        echo "❌ 无效选项"
        ;;
esac