from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.db import models
from jcourse_api.models import Teacher, TeacherEvaluation, Course, Review, Semester
import random
from django.utils import timezone


class Command(BaseCommand):
    help = '将教师评价转换为课程评价'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='限制转换的评价数量 (默认: 100)'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        self.stdout.write(f"开始将教师评价转换为课程评价（限制：{limit}条）...")
        
        # 获取所有小助手用户
        helper_users = list(User.objects.filter(username__startswith='helper').order_by('username'))
        if not helper_users:
            self.stdout.write("❌ 未找到小助手用户，请先运行 create_helpers 命令")
            return
        
        self.stdout.write(f"📋 找到 {len(helper_users)} 个小助手账号")
        
        # 获取有评价内容的教师评价
        evaluations = TeacherEvaluation.objects.filter(
            evaluation_content__isnull=False
        ).exclude(
            evaluation_content__exact=''
        ).order_by('?')[:limit]  # 随机选择
        
        self.stdout.write(f"📊 找到 {evaluations.count()} 条有效评价")
        
        # 获取当前学期（或创建一个默认学期）
        current_semester = Semester.objects.filter(available=True).first()
        if not current_semester:
            current_semester = Semester.objects.create(
                name="2024-2025-1",
                available=True
            )
            self.stdout.write(f"✅ 创建默认学期: {current_semester.name}")
        
        created_reviews = 0
        skipped_reviews = 0
        errors = 0
        
        with transaction.atomic():
            for evaluation in evaluations:
                try:
                    # 查找该教师的课程
                    teacher = evaluation.teacher
                    courses = Course.objects.filter(
                        models.Q(main_teacher=teacher) | models.Q(teacher_group=teacher)
                    ).distinct()
                    
                    if not courses.exists():
                        self.stdout.write(f"⚠️  教师 {teacher.name} 没有关联课程，跳过")
                        skipped_reviews += 1
                        continue
                    
                    # 随机选择一门课程
                    course = random.choice(courses)
                    
                    # 随机选择一个小助手用户
                    helper_user = random.choice(helper_users)
                    
                    # 检查是否已经存在该用户对该课程的评价
                    if Review.objects.filter(user=helper_user, course=course).exists():
                        # 如果已存在，尝试其他用户
                        available_users = [u for u in helper_users 
                                         if not Review.objects.filter(user=u, course=course).exists()]
                        if not available_users:
                            self.stdout.write(f"⚠️  课程 {course.name} 所有小助手都已评价，跳过")
                            skipped_reviews += 1
                            continue
                        helper_user = random.choice(available_users)
                    
                    # 生成随机评分 (3-5分，偏向正面)
                    rating = random.choices([3, 4, 5], weights=[1, 3, 6])[0]
                    
                    # 创建课程评价
                    review = Review.objects.create(
                        user=helper_user,
                        course=course,
                        semester=current_semester,
                        rating=rating,
                        comment=evaluation.evaluation_content,
                        created_at=timezone.now(),
                        score=random.choice(['A', 'B', 'C', 'D', '']) if random.random() > 0.7 else ''
                    )
                    
                    created_reviews += 1
                    
                    if created_reviews % 20 == 0:
                        self.stdout.write(f"📈 已创建 {created_reviews} 条课程评价")
                
                except Exception as e:
                    self.stdout.write(f"❌ 处理教师 {evaluation.teacher.name} 的评价时出错: {e}")
                    errors += 1
                    continue
        
        # 显示统计结果
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 转换完成统计:")
        self.stdout.write(f"✅ 成功创建课程评价: {created_reviews} 条")
        self.stdout.write(f"⚠️  跳过评价: {skipped_reviews} 条")
        self.stdout.write(f"❌ 错误记录: {errors} 条")
        self.stdout.write(f"📈 处理总数: {len(evaluations)} 条")
        self.stdout.write("="*60)
        
        # 显示各用户的评价分布
        self.stdout.write(f"\n📈 用户评价分布:")
        for user in helper_users:
            review_count = Review.objects.filter(user=user).count()
            self.stdout.write(f"{user.username}: {review_count} 条评价")
        
        self.stdout.write(f"\n🎉 转换完成！共创建了 {created_reviews} 条课程评价")