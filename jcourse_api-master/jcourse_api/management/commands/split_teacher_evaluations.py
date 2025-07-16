#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教师评价拆分脚本：将用"|"分割的评价内容拆分为独立的评价记录
"""

import re
from django.core.management.base import BaseCommand
from django.db import transaction
from jcourse_api.models import TeacherEvaluation


class Command(BaseCommand):
    help = '将包含"|"分割的教师评价内容拆分为独立的评价记录'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示将要执行的操作，不实际修改数据库',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='批处理大小（默认：100）',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        
        self.stdout.write(self.style.SUCCESS('开始拆分教师评价数据...'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('这是一次试运行，不会修改数据库'))
        
        # 查找包含"|"的评价记录
        evaluations_with_pipes = TeacherEvaluation.objects.filter(
            evaluation_content__contains='|'
        ).select_related('teacher')
        
        total_count = evaluations_with_pipes.count()
        self.stdout.write(f'找到 {total_count} 条包含"|"分割的评价记录')
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('没有需要拆分的评价记录'))
            return
        
        processed_count = 0
        created_count = 0
        deleted_count = 0
        
        # 批量处理
        for i in range(0, total_count, batch_size):
            batch = evaluations_with_pipes[i:i + batch_size]
            
            with transaction.atomic():
                for evaluation in batch:
                    result = self.split_evaluation(evaluation, dry_run)
                    if result:
                        created_count += result['created']
                        if result['deleted']:
                            deleted_count += 1
                    
                    processed_count += 1
                    
                    # 显示进度
                    if processed_count % 10 == 0:
                        self.stdout.write(f'已处理 {processed_count}/{total_count} 条记录')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'拆分完成！处理了 {processed_count} 条记录，'
                f'创建了 {created_count} 条新记录，'
                f'删除了 {deleted_count} 条原记录'
            )
        )

    def split_evaluation(self, evaluation, dry_run=False):
        """拆分单条评价记录"""
        content = evaluation.evaluation_content.strip()
        
        if not content or '|' not in content:
            return None
        
        # 按 " | " 分割评价内容
        parts = [part.strip() for part in content.split(' | ') if part.strip()]
        
        if len(parts) <= 1:
            return None
        
        self.stdout.write(
            f'拆分教师 {evaluation.teacher.name} 的评价：'
            f'{len(parts)} 条独立评价'
        )
        
        if dry_run:
            for i, part in enumerate(parts, 1):
                self.stdout.write(f'  {i}. {part[:50]}...')
            return {'created': len(parts), 'deleted': True}
        
        # 创建新的独立评价记录
        created_evaluations = []
        for i, part in enumerate(parts):
            # 为每个拆分的评价创建唯一的source_data
            new_source_data = f"{evaluation.source_data}_split_{i+1}"
            
            new_evaluation = TeacherEvaluation.objects.create(
                teacher=evaluation.teacher,
                evaluation_content=part,
                data_sources=evaluation.data_sources,
                evaluation_count=1,  # 每条拆分后的评价都是单独的一条
                source_data=new_source_data,
                created_at=evaluation.created_at,
                updated_at=evaluation.updated_at
            )
            created_evaluations.append(new_evaluation)
        
        # 删除原始的合并评价记录
        evaluation.delete()
        
        return {'created': len(created_evaluations), 'deleted': True}

    def clean_evaluation_content(self, content):
        """清理评价内容"""
        if not content:
            return ''
        
        # 移除多余的空格和换行
        content = re.sub(r'\s+', ' ', content.strip())
        
        # 移除重复的分隔符
        content = re.sub(r'\s*\|\s*\|\s*', ' | ', content)
        
        return content
