#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据整理脚本：将三个CSV文件的数据合并到一张表中
"""

import pandas as pd
import numpy as np

def clean_teacher_name(name):
    """清理教师姓名，去除多余的空格和特殊字符"""
    if pd.isna(name) or name == '':
        return ''
    return str(name).strip()

def merge_evaluations(eval_list):
    """合并多个评价，去除空值"""
    evaluations = []
    for eval_text in eval_list:
        if pd.notna(eval_text) and str(eval_text).strip() != '':
            evaluations.append(str(eval_text).strip())
    return ' | '.join(evaluations) if evaluations else ''

def main():
    print("开始处理数据...")
    
    # 读取三个CSV文件
    try:
        df1 = pd.read_csv('data-1.csv', header=None)
        df2 = pd.read_csv('data-2.csv', header=None)
        df3 = pd.read_csv('data-3.csv', header=None)
        print("成功读取所有CSV文件")
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return
    
    # 处理data-1.csv
    print("处理data-1.csv...")
    data1_records = []
    for index, row in df1.iterrows():
        teacher_name = clean_teacher_name(row[0])
        if teacher_name:
            # 合并所有评价列（除第一列外）
            evaluations = merge_evaluations(row[1:])
            data1_records.append({
                'teacher_name': teacher_name,
                'evaluation': evaluations,
                'source': 'data-1'
            })
    
    # 处理data-2.csv
    print("处理data-2.csv...")
    data2_records = []
    for index, row in df2.iterrows():
        teacher_name = clean_teacher_name(row[0])
        if teacher_name:
            evaluation = str(row[1]).strip() if pd.notna(row[1]) else ''
            data2_records.append({
                'teacher_name': teacher_name,
                'evaluation': evaluation,
                'source': 'data-2'
            })
    
    # 处理data-3.csv
    print("处理data-3.csv...")
    data3_records = []
    for index, row in df3.iterrows():
        teacher_name = clean_teacher_name(row[0])
        if teacher_name:
            # 合并所有评价列（除第一列外）
            evaluations = merge_evaluations(row[1:])
            data3_records.append({
                'teacher_name': teacher_name,
                'evaluation': evaluations,
                'source': 'data-3'
            })
    
    # 合并所有记录
    all_records = data1_records + data2_records + data3_records
    print(f"总共处理了 {len(all_records)} 条记录")
    
    # 创建最终的DataFrame
    final_df = pd.DataFrame(all_records)
    
    # 按教师姓名分组，合并同一教师的所有评价
    print("合并同一教师的评价...")
    grouped_data = []
    
    for teacher_name, group in final_df.groupby('teacher_name'):
        # 合并所有评价
        all_evaluations = []
        sources = []
        
        for _, record in group.iterrows():
            if record['evaluation']:
                all_evaluations.append(record['evaluation'])
                sources.append(record['source'])
        
        combined_evaluation = ' | '.join(all_evaluations)
        combined_sources = ', '.join(set(sources))
        
        grouped_data.append({
            'teacher_name': teacher_name,
            'combined_evaluation': combined_evaluation,
            'data_sources': combined_sources,
            'evaluation_count': len(all_evaluations)
        })
    
    # 创建最终的合并数据表
    merged_df = pd.DataFrame(grouped_data)
    
    # 按教师姓名排序
    merged_df = merged_df.sort_values('teacher_name')
    
    # 添加ID列
    merged_df.insert(0, 'id', range(1, len(merged_df) + 1))
    
    # 保存到新的CSV文件
    output_file = 'merged_teacher_evaluations.csv'
    merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"数据整理完成！")
    print(f"输出文件: {output_file}")
    print(f"总共整理了 {len(merged_df)} 位教师的评价数据")
    print(f"数据表结构:")
    print(f"- id: 序号")
    print(f"- teacher_name: 教师姓名")
    print(f"- combined_evaluation: 合并后的评价内容")
    print(f"- data_sources: 数据来源")
    print(f"- evaluation_count: 评价条数")
    
    # 显示前几行数据作为示例
    print("\n前5行数据示例:")
    print(merged_df.head().to_string(index=False))
    
    # 统计信息
    print(f"\n统计信息:")
    print(f"- 有评价内容的教师: {len(merged_df[merged_df['combined_evaluation'] != ''])} 位")
    print(f"- 无评价内容的教师: {len(merged_df[merged_df['combined_evaluation'] == ''])} 位")
    print(f"- 平均每位教师的评价条数: {merged_df['evaluation_count'].mean():.2f}")

if __name__ == "__main__":
    main()
