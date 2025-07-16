# JCourse 教师评价数据

## 📁 文件说明

- `data-1.csv` - 原始数据文件1
- `data-2.csv` - 原始数据文件2  
- `data-3.csv` - 原始数据文件3
- `merged_teacher_evaluations.csv` - **合并后的数据文件（推荐使用）**
- `merge_data.py` - 数据合并脚本
- `import_to_database.py` - 数据库导入脚本
- `数据导入说明.md` - 详细导入说明文档

## 🚀 快速开始

### 1. 数据概览
合并后的数据包含：
- **1,698** 位教师的评价数据
- **547** 位教师有具体评价内容
- **4,294** 条原始评价记录已去重合并

### 2. 数据结构
```
id,teacher_name,combined_evaluation,data_sources,evaluation_count
1,张三,老师很好 | 给分高,data-1,1
2,李四,讲课清晰 | 平时分高 | 期末简单,"data-1, data-2",2
```

### 3. 快速导入到 SQLite

```bash
# 安装依赖
pip install pandas

# 导入到 SQLite（最简单）
python import_to_database.py

# 指定文件路径
python import_to_database.py --csv merged_teacher_evaluations.csv --sqlite-file jcourse.db
```

### 4. 导入到 MySQL

```bash
# 安装依赖
pip install pandas pymysql sqlalchemy

# 导入到 MySQL
python import_to_database.py \
  --db-type mysql \
  --host localhost \
  --user your_username \
  --password your_password \
  --database jcourse
```

### 5. 导入到 PostgreSQL

```bash
# 安装依赖
pip install pandas psycopg2-binary sqlalchemy

# 导入到 PostgreSQL
python import_to_database.py \
  --db-type postgresql \
  --host localhost \
  --user your_username \
  --password your_password \
  --database jcourse
```

## 📊 数据查询示例

### 基础查询
```sql
-- 查看总记录数
SELECT COUNT(*) FROM teacher_evaluations;

-- 查看前5条记录
SELECT * FROM teacher_evaluations LIMIT 5;

-- 按教师姓名搜索
SELECT * FROM teacher_evaluations WHERE teacher_name LIKE '%张%';
```

### 评价内容搜索
```sql
-- 搜索包含"给分高"的评价
SELECT teacher_name, combined_evaluation 
FROM teacher_evaluations 
WHERE combined_evaluation LIKE '%给分高%';

-- 搜索包含"人好"的评价
SELECT teacher_name, combined_evaluation 
FROM teacher_evaluations 
WHERE combined_evaluation LIKE '%人好%';
```

### 统计分析
```sql
-- 评价数量分布
SELECT evaluation_count, COUNT(*) as teacher_count 
FROM teacher_evaluations 
GROUP BY evaluation_count 
ORDER BY evaluation_count DESC;

-- 数据来源统计
SELECT data_sources, COUNT(*) as count 
FROM teacher_evaluations 
GROUP BY data_sources;

-- 最受好评的教师（包含"好"字最多）
SELECT teacher_name, combined_evaluation,
       (LENGTH(combined_evaluation) - LENGTH(REPLACE(combined_evaluation, '好', ''))) as good_count
FROM teacher_evaluations 
WHERE combined_evaluation IS NOT NULL
ORDER BY good_count DESC
LIMIT 10;
```

## 🔧 自定义导入

如果需要自定义导入逻辑，可以参考以下 Python 代码：

```python
import pandas as pd
import sqlite3

# 读取数据
df = pd.read_csv('merged_teacher_evaluations.csv')

# 数据预处理（可选）
df['teacher_name'] = df['teacher_name'].str.strip()
df['combined_evaluation'] = df['combined_evaluation'].fillna('')

# 连接数据库
conn = sqlite3.connect('jcourse.db')

# 导入数据
df.to_sql('teacher_evaluations', conn, if_exists='replace', index=False)

# 验证
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM teacher_evaluations')
print(f"导入了 {cursor.fetchone()[0]} 条记录")

conn.close()
```

## 📈 数据质量说明

### 数据来源
- `data-1`: 包含教师姓名和多列评价信息
- `data-2`: 包含教师姓名和课程评价
- `data-3`: 包含教师姓名和多列评价信息

### 数据处理
1. **去重合并**: 同一教师的多条评价已合并
2. **来源标记**: 保留了数据来源信息
3. **格式统一**: 所有评价用 " | " 分隔
4. **编码处理**: 使用 UTF-8 编码，支持中文

### 数据限制
- 部分教师只有姓名，没有评价内容
- 评价内容为学生主观评价，仅供参考
- 数据时效性需要定期更新

## 🛠️ 故障排除

### 常见问题

1. **编码错误**
   ```
   UnicodeDecodeError: 'utf-8' codec can't decode
   ```
   解决：确保 CSV 文件使用 UTF-8 编码

2. **数据库连接失败**
   ```
   OperationalError: no such table
   ```
   解决：检查数据库文件路径和权限

3. **依赖包缺失**
   ```
   ModuleNotFoundError: No module named 'pandas'
   ```
   解决：安装所需依赖包

### 获取帮助

```bash
# 查看脚本帮助
python import_to_database.py --help

# 查看详细说明
cat 数据导入说明.md
```

## 📞 联系方式

如有问题或建议，请联系 JCourse 数据团队。

---

**最后更新**: 2025-07-13  
**数据版本**: v1.0
