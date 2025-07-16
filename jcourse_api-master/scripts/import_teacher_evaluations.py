#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教师评价数据导入脚本
将 merged_teacher_evaluations.csv 中的数据导入到 Django 数据库中
"""

import os
import sys
import django
import pandas as pd
from pypinyin import pinyin, lazy_pinyin, Style

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jcourse.settings')
django.setup()

from jcourse_api.models import Teacher, TeacherEvaluation, Department
from django.db import transaction


def get_or_create_teacher(name):
    """获取或创建教师"""
    try:
        # 首先尝试按姓名查找现有教师
        teacher = Teacher.objects.filter(name=name).first()
        if teacher:
            return teacher, False
        
        # 如果不存在，创建新教师
        # 生成拼音
        name_pinyin = ''.join(lazy_pinyin(name))
        abbr_pinyin = ''.join([i[0] for i in pinyin(name, style=Style.FIRST_LETTER)])
        
        teacher = Teacher.objects.create(
            name=name,
            pinyin=name_pinyin,
            abbr_pinyin=abbr_pinyin
        )
        return teacher, True
    except Exception as e:
        print(f"创建教师 {name} 时出错: {e}")
        return None, False


def clean_evaluation_content(content):
    """清理评价内容"""
    if pd.isna(content) or content == '':
        return ''
    
    # 转换为字符串并去除多余空格
    content = str(content).strip()
    
    # 如果内容为空或只包含空白字符，返回空字符串
    if not content or content.isspace():
        return ''
    
    return content


def import_teacher_evaluations(csv_file_path):
    """导入教师评价数据"""
    print(f"🚀 开始导入教师评价数据: {csv_file_path}")
    
    # 检查文件是否存在
    if not os.path.exists(csv_file_path):
        print(f"❌ 文件不存在: {csv_file_path}")
        return False
    
    try:
        # 读取CSV文件
        print("📖 读取CSV文件...")
        df = pd.read_csv(csv_file_path)
        print(f"📊 读取到 {len(df)} 条记录")
        
        # 统计变量
        created_teachers = 0
        created_evaluations = 0
        skipped_records = 0
        error_records = 0
        
        # 使用事务确保数据一致性
        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    # 获取教师姓名
                    teacher_name = str(row['teacher_name']).strip()
                    if not teacher_name or teacher_name == 'nan':
                        print(f"⚠️  第 {index + 1} 行: 教师姓名为空，跳过")
                        skipped_records += 1
                        continue
                    
                    # 获取或创建教师
                    teacher, teacher_created = get_or_create_teacher(teacher_name)
                    if not teacher:
                        print(f"❌ 第 {index + 1} 行: 无法创建教师 {teacher_name}")
                        error_records += 1
                        continue
                    
                    if teacher_created:
                        created_teachers += 1
                        print(f"✅ 创建新教师: {teacher_name}")
                    
                    # 清理评价内容
                    evaluation_content = clean_evaluation_content(row['combined_evaluation'])

                    # 如果没有评价内容，跳过
                    if not evaluation_content:
                        print(f"⚠️  第 {index + 1} 行: 教师 {teacher_name} 没有评价内容，跳过")
                        skipped_records += 1
                        continue

                    # 获取其他字段
                    data_sources = str(row.get('data_sources', '')).strip()

                    # 拆分评价内容（如果包含"|"分隔符）
                    evaluation_parts = [part.strip() for part in evaluation_content.split(' | ') if part.strip()]

                    # 为每个拆分的评价创建独立记录
                    for part_index, part_content in enumerate(evaluation_parts):
                        # 创建唯一标识符用于去重
                        source_data = f"{teacher_name}_{hash(part_content)}_{part_index}"

                        # 检查是否已存在相同的评价
                        existing_evaluation = TeacherEvaluation.objects.filter(
                            teacher=teacher,
                            source_data=source_data
                        ).first()

                        if existing_evaluation:
                            print(f"⚠️  第 {index + 1} 行: 教师 {teacher_name} 的评价片段 {part_index + 1} 已存在，跳过")
                            continue

                        # 创建教师评价记录
                        evaluation = TeacherEvaluation.objects.create(
                            teacher=teacher,
                            evaluation_content=part_content,
                            data_sources=data_sources,
                            evaluation_count=1,  # 每条拆分后的评价都是单独的一条
                            source_data=source_data
                        )

                        created_evaluations += 1
                    
                    # 每100条记录显示一次进度
                    if (index + 1) % 100 == 0:
                        print(f"📈 已处理 {index + 1}/{len(df)} 条记录")
                
                except Exception as e:
                    print(f"❌ 第 {index + 1} 行处理出错: {e}")
                    error_records += 1
                    continue
        
        # 显示导入结果
        print("\n🎉 教师评价数据导入完成！")
        print("=" * 50)
        print(f"📊 导入统计:")
        print(f"  - 总记录数: {len(df)}")
        print(f"  - 创建教师数: {created_teachers}")
        print(f"  - 创建评价数: {created_evaluations}")
        print(f"  - 跳过记录数: {skipped_records}")
        print(f"  - 错误记录数: {error_records}")
        print(f"  - 成功率: {((created_evaluations + skipped_records) / len(df) * 100):.1f}%")
        
        # 显示数据库统计
        total_teachers = Teacher.objects.count()
        total_evaluations = TeacherEvaluation.objects.count()
        teachers_with_evaluations = Teacher.objects.filter(evaluations__isnull=False).distinct().count()
        
        print(f"\n📈 数据库统计:")
        print(f"  - 总教师数: {total_teachers}")
        print(f"  - 总评价数: {total_evaluations}")
        print(f"  - 有评价的教师数: {teachers_with_evaluations}")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入过程中出现错误: {e}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='导入教师评价数据到Django数据库')
    parser.add_argument('csv_file', help='CSV文件路径')
    parser.add_argument('--force', action='store_true', help='强制重新导入（清除现有数据）')
    
    args = parser.parse_args()
    
    # 如果指定了强制导入，先清除现有数据
    if args.force:
        print("⚠️  强制模式：清除现有教师评价数据...")
        TeacherEvaluation.objects.all().delete()
        print("✅ 现有教师评价数据已清除")
    
    # 执行导入
    success = import_teacher_evaluations(args.csv_file)
    
    if success:
        print("\n💡 提示:")
        print("  - 可以通过 Django Admin 查看导入的数据: http://localhost:8000/admin")
        print("  - 教师评价数据已关联到对应的教师记录")
        print("  - 如需重新导入，请使用 --force 参数")
        sys.exit(0)
    else:
        print("\n💥 导入失败，请检查错误信息")
        sys.exit(1)


if __name__ == '__main__':
    main()
