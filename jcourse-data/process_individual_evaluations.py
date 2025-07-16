#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理脚本：将三个CSV文件的数据处理为独立的评价记录，不再合并
"""

import pandas as pd
import numpy as np

def clean_teacher_name(name):
    """清理教师姓名，去除多余的空格和特殊字符"""
    if pd.isna(name) or name == '':
        return ''
    return str(name).strip()

def clean_evaluation_content(content):
    """清理评价内容"""
    if pd.isna(content) or content == '':
        return ''
    return str(content).strip()

def process_data_file(file_path, source_name):
    """处理单个数据文件"""
    print(f"处理文件: {file_path}")

    try:
        # 读取CSV文件，不使用第一行作为列名
        df = pd.read_csv(file_path, header=None)
        print(f"读取到 {len(df)} 条记录")
    except Exception as e:
        print(f"读取文件失败: {e}")
        return []

    records = []

    for index, row in df.iterrows():
        # 第一列是教师姓名
        teacher_name = clean_teacher_name(row.iloc[0] if len(row) > 0 else '')
        if not teacher_name:
            continue

        # 从第二列开始是评价内容，合并所有非空的评价
        evaluations = []
        for col_idx in range(1, len(row)):
            content = clean_evaluation_content(row.iloc[col_idx])
            if content:
                evaluations.append(content)

        # 处理所有评价内容
        for evaluation_content in evaluations:
            if not evaluation_content:
                continue

            # 如果评价内容包含"|"分隔符，拆分为独立评价
            evaluation_parts = [part.strip() for part in evaluation_content.split(' | ') if part.strip()]

            for part in evaluation_parts:
                records.append({
                    'teacher_name': teacher_name,
                    'evaluation_content': part,
                    'data_source': source_name
                })

    print(f"从 {file_path} 提取了 {len(records)} 条独立评价")
    return records

def main():
    print("开始处理教师评价数据...")
    
    # 处理三个数据文件
    all_records = []
    
    # 处理 data-1.csv
    records_1 = process_data_file('data-1.csv', 'data-1')
    all_records.extend(records_1)
    
    # 处理 data-2.csv
    records_2 = process_data_file('data-2.csv', 'data-2')
    all_records.extend(records_2)
    
    # 处理 data-3.csv
    records_3 = process_data_file('data-3.csv', 'data-3')
    all_records.extend(records_3)
    
    print(f"总共处理了 {len(all_records)} 条独立评价记录")
    
    # 创建DataFrame
    final_df = pd.DataFrame(all_records)
    
    # 去重（基于教师姓名和评价内容）
    print("去除重复评价...")
    initial_count = len(final_df)
    final_df = final_df.drop_duplicates(subset=['teacher_name', 'evaluation_content'])
    final_count = len(final_df)
    print(f"去重后剩余 {final_count} 条记录（去除了 {initial_count - final_count} 条重复记录）")
    
    # 按教师分组统计
    teacher_stats = final_df.groupby('teacher_name').size().reset_index(name='evaluation_count')
    print(f"涉及 {len(teacher_stats)} 位教师")
    
    # 为每条记录添加ID
    final_df = final_df.reset_index(drop=True)
    final_df['id'] = final_df.index + 1
    
    # 重新排列列顺序
    final_df = final_df[['id', 'teacher_name', 'evaluation_content', 'data_source']]
    
    # 保存结果
    output_file = 'individual_teacher_evaluations.csv'
    final_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✅ 数据处理完成，结果保存到: {output_file}")
    
    # 显示统计信息
    print("\n=== 统计信息 ===")
    print(f"总评价数: {len(final_df)}")
    print(f"教师数: {len(teacher_stats)}")
    print(f"平均每位教师评价数: {len(final_df) / len(teacher_stats):.2f}")
    
    # 显示评价数最多的前10位教师
    top_teachers = teacher_stats.nlargest(10, 'evaluation_count')
    print("\n评价数最多的前10位教师:")
    for _, row in top_teachers.iterrows():
        print(f"  {row['teacher_name']}: {row['evaluation_count']} 条评价")

if __name__ == '__main__':
    main()
