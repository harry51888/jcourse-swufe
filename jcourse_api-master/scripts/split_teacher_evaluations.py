#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拆分教师评价数据 - 将用"|"分割的评价拆分成独立记录
"""

import os
import sys
import django
from django.db import transaction

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jcourse.settings')
django.setup()

from jcourse_api.models import TeacherEvaluation, Teacher


def main():
    """主函数"""
    print("开始拆分教师评价数据...")
    
    # 检查当前数据状态
    total_evaluations = TeacherEvaluation.objects.count()
    evaluations_with_separator = TeacherEvaluation.objects.filter(evaluation_content__contains='|')
    
    print(f"当前教师评价总数: {total_evaluations}")
    print(f"包含'|'分割符的评价数: {evaluations_with_separator.count()}")
    
    if evaluations_with_separator.count() == 0:
        print("✅ 没有需要拆分的评价数据")
        return
    
    # 显示几个示例
    print("\n包含分割符的评价示例:")
    for eval in evaluations_with_separator[:3]:
        content = eval.evaluation_content
        parts = content.split('|')
        print(f"教师: {eval.teacher_name}")
        print(f"原始内容: {content[:100]}...")
        print(f"可拆分为 {len(parts)} 条评价")
        print("---")
    
    # 执行拆分
    split_evaluations(evaluations_with_separator)
    
    # 验证结果
    print(f"\n拆分完成后的统计:")
    print(f"教师评价总数: {TeacherEvaluation.objects.count()}")
    print(f"包含'|'分割符的评价数: {TeacherEvaluation.objects.filter(evaluation_content__contains='|').count()}")


def split_evaluations(evaluations_with_separator):
    """拆分包含分割符的评价"""
    
    created_count = 0
    processed_count = 0
    
    with transaction.atomic():
        for evaluation in evaluations_with_separator:
            try:
                # 获取原始数据
                teacher = evaluation.teacher
                original_content = evaluation.evaluation_content
                data_sources = evaluation.data_sources
                
                # 按"|"分割评价内容
                parts = original_content.split('|')
                
                # 过滤掉空白内容
                valid_parts = [part.strip() for part in parts if part.strip()]
                
                if len(valid_parts) <= 1:
                    # 如果只有一条评价或没有有效内容，跳过
                    continue
                
                # 删除原始记录
                evaluation.delete()
                
                # 为每个部分创建独立的评价记录
                for i, part in enumerate(valid_parts):
                    # 创建唯一标识符
                    source_data = f"{teacher.name}_{hash(part)}_{i}"
                    
                    # 检查是否已存在相同内容的评价
                    if not TeacherEvaluation.objects.filter(
                        teacher=teacher,
                        evaluation_content=part
                    ).exists():
                        TeacherEvaluation.objects.create(
                            teacher=teacher,
                            teacher_name=teacher.name,
                            evaluation_content=part,
                            evaluation_summary=part[:100] + "..." if len(part) > 100 else part,
                            data_sources=data_sources,
                            evaluation_count=1,
                            source_data=source_data
                        )
                        created_count += 1
                
                processed_count += 1
                
                if processed_count <= 10:  # 只显示前10条处理记录
                    print(f"✅ 拆分教师 {teacher.name} 的评价: {len(valid_parts)} 条")
                elif processed_count == 11:
                    print("... (更多记录处理中)")
                
            except Exception as e:
                print(f"❌ 处理评价时出错: {e}")
                continue
    
    print(f"\n拆分完成:")
    print(f"处理了 {processed_count} 条原始评价")
    print(f"创建了 {created_count} 条独立评价")


if __name__ == '__main__':
    main()
