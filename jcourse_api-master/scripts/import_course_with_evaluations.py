#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入课程数据并关联教师评价
"""

import os
import sys
import django
import pandas as pd
from django.db import transaction

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jcourse.settings')
django.setup()

from jcourse_api.models import Course, Teacher, Department, Category, Semester, TeacherEvaluation


def main():
    """主函数"""
    print("开始导入课程数据并关联教师评价...")
    
    # 检查是否有教师评价数据
    evaluation_count = TeacherEvaluation.objects.count()
    teacher_count = Teacher.objects.count()
    
    print(f"当前数据库状态:")
    print(f"- 教师数量: {teacher_count}")
    print(f"- 教师评价数量: {evaluation_count}")
    
    if evaluation_count == 0:
        print("❌ 没有教师评价数据，请先导入教师评价")
        return
    
    # 获取有评价的教师
    teachers_with_evaluations = Teacher.objects.filter(evaluations__isnull=False).distinct()
    print(f"- 有评价的教师数量: {teachers_with_evaluations.count()}")
    
    # 为有评价的教师创建课程
    create_courses_for_teachers_with_evaluations(teachers_with_evaluations)
    
    print("✅ 课程数据导入完成")


def create_courses_for_teachers_with_evaluations(teachers):
    """为有评价的教师创建课程"""
    
    # 创建学期
    semester, created = Semester.objects.get_or_create(
        name='2024-2025-1',
        defaults={'available': True}
    )
    
    # 获取或创建院系和类别
    departments = get_or_create_departments()
    categories = get_or_create_categories()
    
    # 课程模板数据
    course_templates = [
        ('微观经济学', '经济学院', '专业必修课', 4),
        ('宏观经济学', '经济学院', '专业必修课', 4),
        ('货币银行学', '金融学院', '专业必修课', 3),
        ('投资学', '金融学院', '专业选修课', 3),
        ('公司金融', '金融学院', '专业选修课', 3),
        ('财务管理', '会计学院', '专业必修课', 3),
        ('审计学', '会计学院', '专业必修课', 3),
        ('管理学原理', '工商管理学院', '专业必修课', 3),
        ('市场营销', '工商管理学院', '专业选修课', 3),
        ('人力资源管理', '工商管理学院', '专业选修课', 3),
        ('概率论与数理统计', '统计学院', '专业必修课', 4),
        ('应用统计学', '统计学院', '专业选修课', 3),
        ('数据结构', '信息学院', '专业必修课', 3),
        ('Python程序设计', '信息学院', '专业选修课', 3),
        ('数据库原理', '信息学院', '专业选修课', 3),
        ('经济法', '法学院', '专业选修课', 2),
        ('商法', '法学院', '专业选修课', 2),
        ('马克思主义基本原理', '马克思主义学院', '通识必修课', 3),
        ('毛泽东思想概论', '马克思主义学院', '通识必修课', 3),
        ('大学英语', '外国语学院', '通识必修课', 2),
        ('商务英语', '外国语学院', '通识选修课', 2),
        ('高等数学', '数学学院', '通识必修课', 5),
        ('线性代数', '数学学院', '通识必修课', 3),
        ('计量经济学', '经济学院', '专业必修课', 3),
        ('国际贸易', '经济学院', '专业选修课', 3),
    ]
    
    created_count = 0
    teachers_list = list(teachers)
    
    with transaction.atomic():
        for i, (name, dept_name, cat_name, credit) in enumerate(course_templates):
            if i >= len(teachers_list):
                break
                
            teacher = teachers_list[i]
            
            # 检查院系和类别是否存在
            if dept_name not in departments or cat_name not in categories:
                continue
            
            # 生成课程代码
            dept_code = get_department_code(dept_name)
            course_code = f'{dept_code}{1000 + i:03d}'
            
            # 创建课程
            course, created = Course.objects.get_or_create(
                code=course_code,
                main_teacher=teacher,
                defaults={
                    'name': name,
                    'credit': credit,
                    'department': departments[dept_name],
                    'last_semester': semester,
                }
            )
            
            if created:
                course.categories.add(categories[cat_name])
                course.teacher_group.add(teacher)
                created_count += 1
                
                # 获取该教师的评价数量
                eval_count = teacher.evaluations.count()
                print(f'✅ 创建课程: {name} (教师: {teacher.name}, 评价数: {eval_count})')
    
    print(f'\n创建了 {created_count} 门课程')
    print(f'数据库统计:')
    print(f'课程总数: {Course.objects.count()}')
    print(f'有评价的教师课程数: {Course.objects.filter(main_teacher__evaluations__isnull=False).distinct().count()}')


def get_or_create_departments():
    """获取或创建院系"""
    dept_names = [
        '经济学院', '金融学院', '会计学院', '工商管理学院', '统计学院',
        '信息学院', '法学院', '马克思主义学院', '外国语学院', '数学学院'
    ]
    
    departments = {}
    for name in dept_names:
        dept, created = Department.objects.get_or_create(name=name)
        departments[name] = dept
        if created:
            print(f'✅ 创建院系: {name}')
    
    return departments


def get_or_create_categories():
    """获取或创建课程类别"""
    cat_names = ['专业必修课', '专业选修课', '通识必修课', '通识选修课', '实践课程']
    
    categories = {}
    for name in cat_names:
        cat, created = Category.objects.get_or_create(name=name)
        categories[name] = cat
        if created:
            print(f'✅ 创建课程类别: {name}')
    
    return categories


def get_department_code(dept_name):
    """根据院系名称获取代码"""
    dept_codes = {
        '经济学院': 'ECON',
        '金融学院': 'FIN',
        '会计学院': 'ACC',
        '工商管理学院': 'BUS',
        '统计学院': 'STAT',
        '信息学院': 'INFO',
        '法学院': 'LAW',
        '马克思主义学院': 'MARX',
        '外国语学院': 'LANG',
        '数学学院': 'MATH',
    }
    return dept_codes.get(dept_name, 'MISC')


if __name__ == '__main__':
    main()
