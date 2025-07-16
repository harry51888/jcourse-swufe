#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入独立教师评价数据脚本
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

from jcourse_api.models import Teacher, TeacherEvaluation
from jcourse_api.models.base import Department


def get_or_create_teacher(teacher_name):
    """获取或创建教师"""
    try:
        teacher = Teacher.objects.get(name=teacher_name)
        return teacher, False
    except Teacher.DoesNotExist:
        # 创建新教师
        teacher = Teacher.objects.create(
            name=teacher_name,
            pinyin=teacher_name,  # 简化处理，实际应该转换拼音
            abbr_pinyin=teacher_name[:2],  # 简化处理
            title='教师'
        )
        return teacher, True


def clean_evaluation_content(content):
    """清理评价内容"""
    if pd.isna(content) or content == '':
        return ''
    
    content = str(content).strip()
    if not content or content.isspace():
        return ''
    
    return content


def main():
    """主函数"""
    print("开始导入独立教师评价数据...")
    
    # 读取CSV文件
    csv_file = '../jcourse-data/individual_teacher_evaluations.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ 文件不存在: {csv_file}")
        return
    
    try:
        df = pd.read_csv(csv_file)
        print(f"📖 读取到 {len(df)} 条记录")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return
    
    # 统计变量
    created_teachers = 0
    created_evaluations = 0
    skipped_records = 0
    error_records = 0
    
    print("开始处理数据...")
    
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
                evaluation_content = clean_evaluation_content(row['evaluation_content'])
                
                # 如果没有评价内容，跳过
                if not evaluation_content:
                    print(f"⚠️  第 {index + 1} 行: 教师 {teacher_name} 没有评价内容，跳过")
                    skipped_records += 1
                    continue
                
                # 获取数据来源
                data_source = str(row.get('data_source', '')).strip()
                
                # 创建唯一标识符用于去重
                source_data = f"{teacher_name}_{hash(evaluation_content)}_{index}"
                
                # 检查是否已存在相同的评价
                existing_evaluation = TeacherEvaluation.objects.filter(
                    teacher=teacher,
                    source_data=source_data
                ).first()
                
                if existing_evaluation:
                    print(f"⚠️  第 {index + 1} 行: 教师 {teacher_name} 的评价已存在，跳过")
                    skipped_records += 1
                    continue
                
                # 创建教师评价记录
                evaluation = TeacherEvaluation.objects.create(
                    teacher=teacher,
                    evaluation_content=evaluation_content,
                    data_sources=data_source,
                    evaluation_count=1,  # 每条评价都是独立的
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
    
    # 显示最终统计
    print("\n" + "="*50)
    print("📊 导入完成统计:")
    print(f"✅ 成功创建教师: {created_teachers} 位")
    print(f"✅ 成功创建评价: {created_evaluations} 条")
    print(f"⚠️  跳过记录: {skipped_records} 条")
    print(f"❌ 错误记录: {error_records} 条")
    print(f"📈 处理总数: {len(df)} 条")
    print("="*50)
    
    # 验证导入结果
    total_evaluations = TeacherEvaluation.objects.count()
    total_teachers_with_evaluations = Teacher.objects.filter(evaluations__isnull=False).distinct().count()
    
    print(f"\n🔍 验证结果:")
    print(f"数据库中总评价数: {total_evaluations}")
    print(f"有评价的教师数: {total_teachers_with_evaluations}")
    print(f"平均每位教师评价数: {total_evaluations / total_teachers_with_evaluations:.2f}" if total_teachers_with_evaluations > 0 else "平均每位教师评价数: 0")


if __name__ == '__main__':
    main()
