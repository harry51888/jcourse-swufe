#!/bin/bash

# JCourse-SWUFE 数据库管理脚本
# 用于数据库备份和恢复

echo "🗄️  JCourse-SWUFE 数据库管理"
echo "================================"

# 检查当前目录
if [ ! -d "jcourse_api-master" ] || [ ! -d "jcourse-master" ]; then
    echo "❌ 错误：请在 jcourse-swufe 根目录下运行此脚本"
    exit 1
fi

# 创建备份目录
mkdir -p backups

# 显示菜单
echo ""
echo "请选择操作："
echo "1) 创建数据库备份"
echo "2) 列出现有备份"
echo "3) 恢复数据库备份"
echo "4) 删除旧备份"
echo "5) 数据库状态信息"
echo "0) 退出"
echo ""

read -p "请输入选项 (0-5): " choice

case $choice in
    1)
        echo "📦 创建数据库备份..."
        cd jcourse_api-master
        
        # 生成备份文件名
        BACKUP_FILE="../backups/jcourse_backup_$(date +%Y%m%d_%H%M%S).sql"
        
        # 创建备份
        docker-compose -f docker-compose.dev.yml exec -T db pg_dump -U jcourse jcourse > "$BACKUP_FILE"
        
        if [ $? -eq 0 ]; then
            BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
            echo "✅ 备份创建成功: $BACKUP_FILE ($BACKUP_SIZE)"
        else
            echo "❌ 备份创建失败"
            rm -f "$BACKUP_FILE"
        fi
        
        cd ..
        ;;
    2)
        echo "📋 现有备份列表:"
        if [ "$(ls -A backups/ 2>/dev/null)" ]; then
            ls -lh backups/*.sql 2>/dev/null | awk '{print $9, $5, $6, $7, $8}'
        else
            echo "  📁 无备份文件"
        fi
        ;;
    3)
        echo "🔄 恢复数据库备份..."
        
        # 列出备份文件
        if [ ! "$(ls -A backups/ 2>/dev/null)" ]; then
            echo "❌ 没有找到备份文件"
            exit 1
        fi
        
        echo "可用的备份文件:"
        ls -1 backups/*.sql 2>/dev/null | nl
        echo ""
        read -p "请输入要恢复的备份文件编号: " backup_num
        
        BACKUP_FILE=$(ls -1 backups/*.sql 2>/dev/null | sed -n "${backup_num}p")
        
        if [ -z "$BACKUP_FILE" ]; then
            echo "❌ 无效的备份文件编号"
            exit 1
        fi
        
        echo "警告：此操作将覆盖当前数据库！"
        read -p "确认恢复备份 $BACKUP_FILE? (y/N): " confirm
        
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            cd jcourse_api-master
            
            # 先删除现有数据库
            docker-compose -f docker-compose.dev.yml exec -T db dropdb -U jcourse jcourse
            docker-compose -f docker-compose.dev.yml exec -T db createdb -U jcourse jcourse
            
            # 恢复备份
            docker-compose -f docker-compose.dev.yml exec -T db psql -U jcourse jcourse < "../$BACKUP_FILE"
            
            if [ $? -eq 0 ]; then
                echo "✅ 数据库恢复成功"
            else
                echo "❌ 数据库恢复失败"
            fi
            
            cd ..
        else
            echo "取消恢复操作"
        fi
        ;;
    4)
        echo "🗑️  删除旧备份..."
        
        if [ ! "$(ls -A backups/ 2>/dev/null)" ]; then
            echo "📁 没有备份文件需要删除"
            exit 0
        fi
        
        echo "当前备份文件:"
        ls -lh backups/*.sql 2>/dev/null | awk '{print NR")", $9, $5, $6, $7, $8}'
        echo ""
        
        read -p "保留最近的几个备份? (默认: 5): " keep_count
        keep_count=${keep_count:-5}
        
        # 删除旧备份，保留最新的几个
        ls -t backups/*.sql 2>/dev/null | tail -n +$((keep_count + 1)) | xargs rm -f
        
        remaining=$(ls backups/*.sql 2>/dev/null | wc -l)
        echo "✅ 清理完成，保留 $remaining 个备份文件"
        ;;
    5)
        echo "📊 数据库状态信息:"
        cd jcourse_api-master
        
        echo ""
        echo "Docker 容器状态:"
        docker-compose -f docker-compose.dev.yml ps
        
        echo ""
        echo "数据库连接信息:"
        docker-compose -f docker-compose.dev.yml exec db psql -U jcourse jcourse -c "\l"
        
        echo ""
        echo "数据库表信息:"
        docker-compose -f docker-compose.dev.yml exec db psql -U jcourse jcourse -c "\dt"
        
        echo ""
        echo "数据库大小:"
        docker-compose -f docker-compose.dev.yml exec db psql -U jcourse jcourse -c "SELECT pg_size_pretty(pg_database_size('jcourse'));"
        
        cd ..
        ;;
    0)
        echo "👋 退出数据库管理"
        ;;
    *)
        echo "❌ 无效选项"
        ;;
esac