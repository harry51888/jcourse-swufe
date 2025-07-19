#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建多个小助手用户账号脚本
"""

import os
import sys
import django
from django.contrib.auth.models import User
from django.db import transaction

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jcourse.settings')
django.setup()

from oauth.models import UserProfile


def create_helper_users():
    """创建多个小助手用户账号"""
    print("开始创建小助手用户账号...")
    
    # 定义小助手账号信息
    helper_users = [
        {'username': 'helper001', 'email': 'helper001@swufe.edu.cn', 'nickname': '课程小助手01'},
        {'username': 'helper002', 'email': 'helper002@swufe.edu.cn', 'nickname': '课程小助手02'},
        {'username': 'helper003', 'email': 'helper003@swufe.edu.cn', 'nickname': '课程小助手03'},
        {'username': 'helper004', 'email': 'helper004@swufe.edu.cn', 'nickname': '课程小助手04'},
        {'username': 'helper005', 'email': 'helper005@swufe.edu.cn', 'nickname': '课程小助手05'},
        {'username': 'helper006', 'email': 'helper006@swufe.edu.cn', 'nickname': '课程小助手06'},
        {'username': 'helper007', 'email': 'helper007@swufe.edu.cn', 'nickname': '课程小助手07'},
        {'username': 'helper008', 'email': 'helper008@swufe.edu.cn', 'nickname': '课程小助手08'},
        {'username': 'helper009', 'email': 'helper009@swufe.edu.cn', 'nickname': '课程小助手09'},
        {'username': 'helper010', 'email': 'helper010@swufe.edu.cn', 'nickname': '课程小助手10'},
    ]
    
    default_password = 'helper123456'
    created_count = 0
    existing_count = 0
    
    with transaction.atomic():
        for helper_info in helper_users:
            try:
                # 检查用户是否已存在
                if User.objects.filter(username=helper_info['username']).exists():
                    print(f"⚠️  用户 {helper_info['username']} 已存在，跳过")
                    existing_count += 1
                    continue
                
                # 创建用户
                user = User.objects.create_user(
                    username=helper_info['username'],
                    email=helper_info['email'],
                    password=default_password,
                    first_name=helper_info['nickname'],
                    is_active=True
                )
                
                # 创建用户档案
                profile = UserProfile.objects.create(
                    user=user,
                    user_type='helper'
                )
                
                print(f"✅ 成功创建用户: {helper_info['username']} ({helper_info['nickname']})")
                created_count += 1
                
            except Exception as e:
                print(f"❌ 创建用户 {helper_info['username']} 失败: {e}")
    
    # 显示统计结果
    print("\n" + "="*50)
    print("📊 用户创建统计:")
    print(f"✅ 成功创建: {created_count} 个")
    print(f"⚠️  已存在: {existing_count} 个")
    print(f"📈 总计: {len(helper_users)} 个")
    print("="*50)
    
    # 显示登录信息
    if created_count > 0:
        print(f"\n🔑 登录信息:")
        print(f"用户名: helper001 ~ helper{len(helper_users):03d}")
        print(f"默认密码: {default_password}")
        print(f"邮箱: helper[编号]@swufe.edu.cn")


if __name__ == '__main__':
    create_helper_users()