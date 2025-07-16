#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JCourse 教师评价数据导入脚本
支持 MySQL、PostgreSQL、SQLite 数据库
"""

import pandas as pd
import sqlite3
import argparse
import sys
import os
from pathlib import Path

def create_table_sqlite(conn):
    """创建 SQLite 数据表"""
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teacher_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT NOT NULL,
            combined_evaluation TEXT,
            data_sources TEXT,
            evaluation_count INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_teacher_name ON teacher_evaluations(teacher_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_evaluation_count ON teacher_evaluations(evaluation_count)')
    
    conn.commit()
    print("✅ SQLite 表和索引创建成功")

def create_table_mysql(conn):
    """创建 MySQL 数据表"""
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teacher_evaluations (
            id INT PRIMARY KEY AUTO_INCREMENT,
            teacher_name VARCHAR(100) NOT NULL,
            combined_evaluation TEXT,
            data_sources VARCHAR(50),
            evaluation_count INT NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_teacher_name (teacher_name),
            INDEX idx_evaluation_count (evaluation_count),
            FULLTEXT idx_evaluation_content (combined_evaluation)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    
    conn.commit()
    print("✅ MySQL 表和索引创建成功")

def create_table_postgresql(conn):
    """创建 PostgreSQL 数据表"""
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teacher_evaluations (
            id SERIAL PRIMARY KEY,
            teacher_name VARCHAR(100) NOT NULL,
            combined_evaluation TEXT,
            data_sources VARCHAR(50),
            evaluation_count INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_teacher_name ON teacher_evaluations(teacher_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_evaluation_count ON teacher_evaluations(evaluation_count)')
    
    conn.commit()
    print("✅ PostgreSQL 表和索引创建成功")

def import_to_sqlite(csv_file, db_file):
    """导入数据到 SQLite"""
    try:
        # 读取 CSV 文件
        print(f"📖 正在读取 CSV 文件: {csv_file}")
        df = pd.read_csv(csv_file)
        print(f"📊 读取到 {len(df)} 条记录")
        
        # 连接数据库
        print(f"🔗 连接到 SQLite 数据库: {db_file}")
        conn = sqlite3.connect(db_file)
        
        # 创建表
        create_table_sqlite(conn)
        
        # 导入数据
        print("📥 正在导入数据...")
        df.to_sql('teacher_evaluations', conn, if_exists='replace', index=False)
        
        # 验证导入
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM teacher_evaluations')
        count = cursor.fetchone()[0]
        print(f"✅ 数据导入成功！共导入 {count} 条记录")
        
        # 显示统计信息
        cursor.execute('SELECT COUNT(*) FROM teacher_evaluations WHERE combined_evaluation IS NOT NULL AND combined_evaluation != ""')
        eval_count = cursor.fetchone()[0]
        print(f"📈 其中有评价内容的记录: {eval_count} 条")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        return False

def import_to_mysql(csv_file, host, port, user, password, database):
    """导入数据到 MySQL"""
    try:
        import pymysql
        
        # 读取 CSV 文件
        print(f"📖 正在读取 CSV 文件: {csv_file}")
        df = pd.read_csv(csv_file)
        print(f"📊 读取到 {len(df)} 条记录")
        
        # 连接数据库
        print(f"🔗 连接到 MySQL 数据库: {host}:{port}/{database}")
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        # 创建表
        create_table_mysql(conn)
        
        # 导入数据
        print("📥 正在导入数据...")
        from sqlalchemy import create_engine
        engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4')
        df.to_sql('teacher_evaluations', engine, if_exists='replace', index=False)
        
        # 验证导入
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM teacher_evaluations')
        count = cursor.fetchone()[0]
        print(f"✅ 数据导入成功！共导入 {count} 条记录")
        
        conn.close()
        return True
        
    except ImportError:
        print("❌ 请安装 pymysql: pip install pymysql")
        return False
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        return False

def import_to_postgresql(csv_file, host, port, user, password, database):
    """导入数据到 PostgreSQL"""
    try:
        import psycopg2
        
        # 读取 CSV 文件
        print(f"📖 正在读取 CSV 文件: {csv_file}")
        df = pd.read_csv(csv_file)
        print(f"📊 读取到 {len(df)} 条记录")
        
        # 连接数据库
        print(f"🔗 连接到 PostgreSQL 数据库: {host}:{port}/{database}")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        # 创建表
        create_table_postgresql(conn)
        
        # 导入数据
        print("📥 正在导入数据...")
        from sqlalchemy import create_engine
        engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')
        df.to_sql('teacher_evaluations', engine, if_exists='replace', index=False)
        
        # 验证导入
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM teacher_evaluations')
        count = cursor.fetchone()[0]
        print(f"✅ 数据导入成功！共导入 {count} 条记录")
        
        conn.close()
        return True
        
    except ImportError:
        print("❌ 请安装 psycopg2: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='JCourse 教师评价数据导入工具')
    parser.add_argument('--csv', default='merged_teacher_evaluations.csv', help='CSV 文件路径')
    parser.add_argument('--db-type', choices=['sqlite', 'mysql', 'postgresql'], default='sqlite', help='数据库类型')
    
    # SQLite 参数
    parser.add_argument('--sqlite-file', default='jcourse.db', help='SQLite 数据库文件路径')
    
    # MySQL/PostgreSQL 参数
    parser.add_argument('--host', default='localhost', help='数据库主机')
    parser.add_argument('--port', type=int, help='数据库端口')
    parser.add_argument('--user', help='数据库用户名')
    parser.add_argument('--password', help='数据库密码')
    parser.add_argument('--database', help='数据库名称')
    
    args = parser.parse_args()
    
    # 检查 CSV 文件是否存在
    if not os.path.exists(args.csv):
        print(f"❌ CSV 文件不存在: {args.csv}")
        sys.exit(1)
    
    print("🚀 JCourse 教师评价数据导入工具")
    print("=" * 50)
    
    success = False
    
    if args.db_type == 'sqlite':
        success = import_to_sqlite(args.csv, args.sqlite_file)
        
    elif args.db_type == 'mysql':
        if not all([args.user, args.password, args.database]):
            print("❌ MySQL 需要提供 --user, --password, --database 参数")
            sys.exit(1)
        port = args.port or 3306
        success = import_to_mysql(args.csv, args.host, port, args.user, args.password, args.database)
        
    elif args.db_type == 'postgresql':
        if not all([args.user, args.password, args.database]):
            print("❌ PostgreSQL 需要提供 --user, --password, --database 参数")
            sys.exit(1)
        port = args.port or 5432
        success = import_to_postgresql(args.csv, args.host, port, args.user, args.password, args.database)
    
    if success:
        print("\n🎉 数据导入完成！")
        print("\n💡 建议执行以下查询验证数据：")
        print("   SELECT COUNT(*) FROM teacher_evaluations;")
        print("   SELECT * FROM teacher_evaluations LIMIT 5;")
    else:
        print("\n💥 数据导入失败，请检查错误信息")
        sys.exit(1)

if __name__ == '__main__':
    main()
