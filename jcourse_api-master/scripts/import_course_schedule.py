#!/usr/bin/env python3
"""
导入课表数据脚本
适配新的课表CSV格式
"""
import os
import sys
import csv
import django
from pathlib import Path

# 添加项目根目录到Python路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jcourse.settings')
django.setup()

from jcourse_api.models import Course, Teacher, Department, Category, Semester
from pypinyin import pinyin, lazy_pinyin, Style


def get_or_create_department(name):
    """获取或创建院系"""
    department, created = Department.objects.get_or_create(name=name)
    if created:
        print(f"创建新院系: {name}")
    return department


def get_or_create_category(name):
    """获取或创建课程类别"""
    category, created = Category.objects.get_or_create(name=name)
    if created:
        print(f"创建新类别: {name}")
    return category


def get_or_create_teacher(name, department):
    """获取或创建教师"""
    # 生成拼音
    name_pinyin = ''.join(lazy_pinyin(name))
    abbr_pinyin = ''.join([i[0] for i in pinyin(name, style=Style.FIRST_LETTER)])
    
    teacher, created = Teacher.objects.get_or_create(
        name=name,
        defaults={
            'department': department,
            'pinyin': name_pinyin,
            'abbr_pinyin': abbr_pinyin
        }
    )
    if created:
        print(f"创建新教师: {name} ({department.name})")
    return teacher


def get_or_create_semester(name):
    """获取或创建学期"""
    semester, created = Semester.objects.get_or_create(name=name)
    if created:
        print(f"创建新学期: {name}")
    return semester


def map_course_nature_to_category(nature):
    """将课程性质映射到类别"""
    mapping = {
        '通识基础课': '通识',
        '专业方向课': '专业',
        '实践环节课': '实践',
        '专业核心课': '专业',
        '专业基础课': '专业',
        '通识选修课': '通选',
        '体育课': '体育',
        '新生研讨课': '新生研讨',
    }
    return mapping.get(nature, '其他')


def import_course_data(csv_file_path, semester_name):
    """导入课表数据"""
    semester = get_or_create_semester(semester_name)
    
    imported_count = 0
    skipped_count = 0
    
    with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # 提取数据
                course_code = row['课程代码']
                course_name = row['课程名称']
                course_nature = row['课程性质']
                department_name = row['开课学院']
                teacher_name = row['任课老师']
                credit = float(row['学分'])
                
                # 跳过空数据
                if not course_code or not course_name or not teacher_name:
                    skipped_count += 1
                    continue
                
                # 创建或获取相关对象
                department = get_or_create_department(department_name)
                teacher = get_or_create_teacher(teacher_name, department)
                category_name = map_course_nature_to_category(course_nature)
                category = get_or_create_category(category_name)
                
                # 检查课程是否已存在
                existing_course = Course.objects.filter(
                    code=course_code,
                    main_teacher=teacher
                ).first()
                
                if existing_course:
                    # 更新现有课程
                    existing_course.name = course_name
                    existing_course.credit = credit
                    existing_course.department = department
                    existing_course.last_semester = semester
                    existing_course.save()
                    existing_course.categories.add(category)
                    existing_course.teacher_group.add(teacher)
                    print(f"更新课程: {course_code} - {course_name}")
                else:
                    # 创建新课程
                    course = Course.objects.create(
                        code=course_code,
                        name=course_name,
                        credit=credit,
                        department=department,
                        main_teacher=teacher,
                        last_semester=semester
                    )
                    course.categories.add(category)
                    course.teacher_group.add(teacher)
                    print(f"创建新课程: {course_code} - {course_name}")
                
                imported_count += 1
                
            except Exception as e:
                print(f"处理行时出错: {row}, 错误: {e}")
                skipped_count += 1
                continue
    
    print(f"\n导入完成!")
    print(f"成功导入: {imported_count} 门课程")
    print(f"跳过: {skipped_count} 条记录")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python import_course_schedule.py <CSV文件路径> <学期名称>")
        print("例如: python import_course_schedule.py ../课表数据/2024-2025-1课表.csv 2024-2025-1")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    semester = sys.argv[2]
    
    if not os.path.exists(csv_file):
        print(f"文件不存在: {csv_file}")
        sys.exit(1)
    
    print(f"开始导入课表数据...")
    print(f"文件: {csv_file}")
    print(f"学期: {semester}")
    print("-" * 50)
    
    import_course_data(csv_file, semester)
