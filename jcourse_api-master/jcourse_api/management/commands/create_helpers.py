from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from oauth.models import UserProfile
from django.db import transaction


class Command(BaseCommand):
    help = '创建小助手用户账号'

    def handle(self, *args, **options):
        self.stdout.write("开始创建小助手用户账号...")
        
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
                        self.stdout.write(f"⚠️  用户 {helper_info['username']} 已存在，跳过")
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
                    
                    self.stdout.write(f"✅ 成功创建用户: {helper_info['username']} ({helper_info['nickname']})")
                    created_count += 1
                    
                except Exception as e:
                    self.stdout.write(f"❌ 创建用户 {helper_info['username']} 失败: {e}")
        
        # 显示统计结果
        self.stdout.write("\n" + "="*50)
        self.stdout.write("📊 用户创建统计:")
        self.stdout.write(f"✅ 成功创建: {created_count} 个")
        self.stdout.write(f"⚠️  已存在: {existing_count} 个")
        self.stdout.write(f"📈 总计: {len(helper_users)} 个")
        self.stdout.write("="*50)
        
        # 显示登录信息
        if created_count > 0:
            self.stdout.write(f"\n🔑 登录信息:")
            self.stdout.write(f"用户名: helper001 ~ helper{len(helper_users):03d}")
            self.stdout.write(f"默认密码: {default_password}")
            self.stdout.write(f"邮箱: helper[编号]@swufe.edu.cn")