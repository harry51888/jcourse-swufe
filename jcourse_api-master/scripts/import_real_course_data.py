#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从真实课表数据导入课程，并关联已有的教师评价
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
    print("开始从真实课表数据导入课程...")
    
    # 清除之前创建的虚假课程数据
    print("清除之前的课程数据...")
    Course.objects.all().delete()
    
    # 检查教师评价数据
    evaluation_count = TeacherEvaluation.objects.count()
    teacher_count = Teacher.objects.count()
    
    print(f"当前数据库状态:")
    print(f"- 教师数量: {teacher_count}")
    print(f"- 教师评价数量: {evaluation_count}")
    
    # 导入课表数据
    course_files = [
        '../课表数据/2024-2025-1课表(20241129).csv',
        '../课表数据/2024-2025-2课表(20250324)-3.csv',
        '../课表数据/2025-2026-1课表(20250620).csv'
    ]
    
    total_imported = 0
    for file_path in course_files:
        if os.path.exists(file_path):
            imported = import_courses_from_file(file_path)
            total_imported += imported
            print(f"从 {file_path} 导入了 {imported} 门课程")
        else:
            print(f"⚠️  文件不存在: {file_path}")
    
    print(f"\n✅ 总共导入了 {total_imported} 门课程")
    print(f"数据库统计:")
    print(f"- 课程总数: {Course.objects.count()}")
    print(f"- 有评价的课程数: {Course.objects.filter(main_teacher__evaluations__isnull=False).distinct().count()}")


def import_courses_from_file(file_path):
    """从单个课表文件导入课程"""
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"读取文件: {file_path}, 共 {len(df)} 条记录")
        
        # 检查列名
        required_columns = ['课程代码', '课程名称', '任课老师', '开课学院', '学分', '课程性质']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"⚠️  缺少必要列: {missing_columns}")
            print(f"可用列: {list(df.columns)}")
            return 0
        
        # 获取或创建学期
        semester_name = extract_semester_from_filename(file_path)
        semester, created = Semester.objects.get_or_create(
            name=semester_name,
            defaults={'available': True}
        )
        if created:
            print(f"✅ 创建学期: {semester_name}")
        
        # 获取或创建院系和类别
        departments = get_or_create_departments_from_data(df)
        categories = get_or_create_categories_from_data(df)
        
        imported_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    # 提取课程信息
                    course_code = str(row['课程代码']).strip()
                    course_name = str(row['课程名称']).strip()
                    teacher_name = str(row['任课老师']).strip()
                    department_name = str(row['开课学院']).strip()
                    credit = float(row['学分']) if pd.notna(row['学分']) else 0.0
                    course_type = str(row['课程性质']).strip()
                    
                    # 跳过无效数据
                    if not course_code or not course_name or not teacher_name:
                        skipped_count += 1
                        continue
                    
                    # 获取或创建教师
                    teacher = get_or_create_teacher(teacher_name)
                    
                    # 获取或创建院系
                    department = departments.get(department_name)
                    if not department:
                        department, created = Department.objects.get_or_create(name=department_name)
                        departments[department_name] = department
                    
                    # 获取或创建课程类别
                    category = categories.get(course_type)
                    if not category:
                        category, created = Category.objects.get_or_create(name=course_type)
                        categories[course_type] = category
                    
                    # 创建课程
                    course, created = Course.objects.get_or_create(
                        code=course_code,
                        main_teacher=teacher,
                        defaults={
                            'name': course_name,
                            'credit': credit,
                            'department': department,
                            'last_semester': semester,
                        }
                    )
                    
                    if created:
                        course.categories.add(category)
                        course.teacher_group.add(teacher)
                        imported_count += 1
                        
                        # 检查教师是否有评价
                        eval_count = teacher.evaluations.count()
                        status = f"(有{eval_count}条评价)" if eval_count > 0 else "(无评价)"
                        
                        if imported_count <= 10:  # 只显示前10条
                            print(f"✅ 导入课程: {course_name} - {teacher_name} {status}")
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    print(f"❌ 第 {index + 1} 行处理出错: {e}")
                    skipped_count += 1
        
        print(f"导入完成: {imported_count} 门课程, 跳过: {skipped_count} 条记录")
        return imported_count
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return 0


def extract_semester_from_filename(file_path):
    """从文件名提取学期"""
    filename = os.path.basename(file_path)
    if '2024-2025-1' in filename:
        return '2024-2025-1'
    elif '2024-2025-2' in filename:
        return '2024-2025-2'
    elif '2025-2026-1' in filename:
        return '2025-2026-1'
    else:
        return '2024-2025-1'  # 默认学期


def get_or_create_teacher(teacher_name):
    """获取或创建教师"""
    teacher, created = Teacher.objects.get_or_create(
        name=teacher_name,
        defaults={
            'pinyin': teacher_name,
            'abbr_pinyin': teacher_name[:2] if len(teacher_name) >= 2 else teacher_name,
            'title': '教师'
        }
    )
    return teacher


def get_or_create_departments_from_data(df):
    """从数据中获取或创建院系"""
    departments = {}
    unique_departments = df['开课学院'].dropna().unique()
    
    for dept_name in unique_departments:
        dept_name = str(dept_name).strip()
        if dept_name:
            dept, created = Department.objects.get_or_create(name=dept_name)
            departments[dept_name] = dept
            if created:
                print(f"✅ 创建院系: {dept_name}")
    
    return departments


def get_or_create_categories_from_data(df):
    """从数据中获取或创建课程类别"""
    categories = {}
    unique_categories = df['课程性质'].dropna().unique()
    
    for cat_name in unique_categories:
        cat_name = str(cat_name).strip()
        if cat_name:
            cat, created = Category.objects.get_or_create(name=cat_name)
            categories[cat_name] = cat
            if created:
                print(f"✅ 创建课程类别: {cat_name}")
    
    return categories


if __name__ == '__main__':
    main()
