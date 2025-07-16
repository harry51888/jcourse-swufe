#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将教师评价数据作为课程点评导入脚本
将 merged_teacher_evaluations.csv 中的数据作为学生点评导入到 Review 模型中
"""

import os
import sys
import pandas as pd
import random
from datetime import datetime, timedelta

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jcourse.settings')

import django
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from jcourse_api.models import Teacher, Course, Review, Semester
from django.db import transaction


def get_or_create_helper_user():
    """获取或创建小助手用户用于导入评价"""
    username = '小助手'
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': 'helper@swufe.edu.cn',
            'first_name': '小',
            'last_name': '助手',
            'is_active': True
        }
    )
    if created:
        print(f"✅ 创建小助手用户: {username}")
    return user


def find_courses_by_teacher(teacher_name):
    """根据教师姓名查找相关课程"""
    try:
        # 查找教师
        teachers = Teacher.objects.filter(name__icontains=teacher_name.strip())
        if not teachers.exists():
            return []
        
        courses = []
        for teacher in teachers:
            # 查找该教师作为主讲教师的课程
            main_courses = Course.objects.filter(main_teacher=teacher)
            courses.extend(main_courses)
            
            # 查找该教师参与的课程
            group_courses = Course.objects.filter(teacher_group=teacher)
            courses.extend(group_courses)
        
        # 去重
        unique_courses = list(set(courses))
        return unique_courses
    except Exception as e:
        print(f"查找教师 {teacher_name} 的课程时出错: {e}")
        return []


def clean_evaluation_content(content):
    """清理评价内容"""
    if pd.isna(content) or content == '':
        return ''
    
    content = str(content).strip()
    if not content or content.isspace():
        return ''
    
    return content


def split_evaluation_content(content):
    """将评价内容按 | 分割成多个独立评价"""
    if not content:
        return []
    
    # 按 " | " 分割
    parts = content.split(' | ')
    evaluations = []
    
    for part in parts:
        part = part.strip()
        if part and len(part) > 5:  # 过滤太短的评价
            evaluations.append(part)
    
    return evaluations


def generate_rating_from_content(content):
    """根据评价内容生成推荐指数"""
    positive_keywords = ['好', '棒', '优秀', '推荐', '不错', '很好', '给分高', '简单', '容易', '人好']
    negative_keywords = ['差', '烂', '难', '坑', '不推荐', '给分低', '严格', '变态']
    
    content_lower = content.lower()
    
    positive_count = sum(1 for keyword in positive_keywords if keyword in content)
    negative_count = sum(1 for keyword in negative_keywords if keyword in content)
    
    if positive_count > negative_count:
        return random.choice([4, 5])  # 正面评价给4-5分
    elif negative_count > positive_count:
        return random.choice([1, 2])  # 负面评价给1-2分
    else:
        return random.choice([3, 4])  # 中性评价给3-4分


def get_random_semester():
    """获取一个随机的学期"""
    semesters = Semester.objects.all()
    if semesters.exists():
        return random.choice(semesters)
    return None


def import_reviews_from_evaluations(csv_file_path):
    """将教师评价数据作为课程点评导入"""
    print(f"🚀 开始将教师评价数据作为课程点评导入: {csv_file_path}")
    
    # 检查文件是否存在
    if not os.path.exists(csv_file_path):
        print(f"❌ 文件不存在: {csv_file_path}")
        return False
    
    try:
        # 读取CSV文件
        print("📖 读取CSV文件...")
        df = pd.read_csv(csv_file_path)
        print(f"📊 读取到 {len(df)} 条记录")
        
        # 获取小助手用户
        helper_user = get_or_create_helper_user()

        # 统计变量
        created_reviews = 0
        skipped_records = 0
        error_records = 0

        # 分批处理，避免事务过大
        for index, row in df.iterrows():
                try:
                    # 获取教师姓名
                    teacher_name = str(row['teacher_name']).strip()
                    if not teacher_name or teacher_name == 'nan':
                        skipped_records += 1
                        continue
                    
                    # 清理评价内容
                    evaluation_content = clean_evaluation_content(row['combined_evaluation'])
                    if not evaluation_content:
                        skipped_records += 1
                        continue
                    
                    # 查找该教师的课程
                    courses = find_courses_by_teacher(teacher_name)
                    if not courses:
                        print(f"⚠️  第 {index + 1} 行: 未找到教师 {teacher_name} 的课程")
                        skipped_records += 1
                        continue
                    
                    # 分割评价内容
                    individual_evaluations = split_evaluation_content(evaluation_content)
                    if not individual_evaluations:
                        skipped_records += 1
                        continue
                    
                    # 选择一门课程来添加评价
                    if courses:
                        course = courses[0]  # 选择第一门课程

                        # 检查小助手是否已经对该课程有点评
                        existing_review = Review.objects.filter(
                            user=helper_user,
                            course=course
                        ).first()

                        if existing_review:
                            # 如果已有点评，更新评价内容
                            try:
                                # 合并评价内容
                                new_content = evaluation_content
                                if existing_review.comment and existing_review.comment.strip():
                                    new_content = existing_review.comment + " | " + evaluation_content

                                # 限制评价长度
                                if len(new_content) > 9000:
                                    new_content = new_content[:9000] + "..."

                                existing_review.comment = new_content
                                existing_review.save()

                                print(f"📝 更新课程 {course.name} 的评价")
                                created_reviews += 1

                            except Exception as e:
                                print(f"❌ 更新点评时出错: {e}")
                                error_records += 1
                        else:
                            # 创建新的点评记录
                            try:

                                # 生成推荐指数
                                rating = generate_rating_from_content(evaluation_content)

                                # 获取随机学期
                                semester = get_random_semester()

                                # 生成随机的创建时间（过去1年内）
                                days_ago = random.randint(1, 365)
                                created_time = timezone.now() - timedelta(days=days_ago)

                                # 创建点评记录
                                review = Review.objects.create(
                                    user=helper_user,
                                    course=course,
                                    semester=semester,
                                    rating=rating,
                                    comment=evaluation_content,
                                    created_at=created_time,
                                    modified_at=created_time
                                )

                                print(f"✅ 为课程 {course.name} 创建新评价")
                                created_reviews += 1

                            except Exception as e:
                                print(f"❌ 创建点评时出错: {e}")
                                error_records += 1

                    if created_reviews % 50 == 0 and created_reviews > 0:
                        print(f"📈 已处理 {created_reviews} 条点评")
                    
                    # 每100条记录显示一次进度
                    if (index + 1) % 100 == 0:
                        print(f"📈 已处理 {index + 1}/{len(df)} 条记录")
                
                except Exception as e:
                    print(f"❌ 第 {index + 1} 行处理出错: {e}")
                    error_records += 1
                    continue
        
        # 显示导入结果
        print("\n🎉 教师评价数据作为课程点评导入完成！")
        print("=" * 60)
        print(f"📊 导入统计:")
        print(f"  - 总记录数: {len(df)}")
        print(f"  - 创建点评数: {created_reviews}")
        print(f"  - 跳过记录数: {skipped_records}")
        print(f"  - 错误记录数: {error_records}")
        print(f"  - 成功率: {(created_reviews / len(df) * 100):.1f}%")
        
        # 显示数据库统计
        total_reviews = Review.objects.count()
        total_courses = Course.objects.count()
        courses_with_reviews = Course.objects.filter(review_count__gt=0).count()
        
        print(f"\n📈 数据库统计:")
        print(f"  - 总点评数: {total_reviews}")
        print(f"  - 总课程数: {total_courses}")
        print(f"  - 有点评的课程数: {courses_with_reviews}")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入过程中出现错误: {e}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='将教师评价数据作为课程点评导入到Django数据库')
    parser.add_argument('csv_file', help='CSV文件路径')
    parser.add_argument('--force', action='store_true', help='强制重新导入（清除现有匿名点评）')
    
    args = parser.parse_args()
    
    # 如果指定了强制导入，先清除现有小助手点评
    if args.force:
        print("⚠️  强制模式：清除现有小助手点评数据...")
        helper_user = User.objects.filter(username='小助手').first()
        if helper_user:
            Review.objects.filter(user=helper_user).delete()
            print("✅ 现有小助手点评数据已清除")
    
    # 执行导入
    success = import_reviews_from_evaluations(args.csv_file)
    
    if success:
        print("\n💡 提示:")
        print("  - 可以通过前端页面查看导入的点评: http://localhost:3000")
        print("  - 可以通过 Django Admin 管理点评数据: http://localhost:8000/admin")
        print("  - 点评数据已关联到对应的课程记录")
        print("  - 如需重新导入，请使用 --force 参数")
        sys.exit(0)
    else:
        print("\n💥 导入失败，请检查错误信息")
        sys.exit(1)


if __name__ == '__main__':
    main()
