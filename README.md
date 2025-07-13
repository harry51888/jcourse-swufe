# JCourse 课程评价系统

一个基于 Django + Next.js 的课程评价系统，支持课程搜索、评价和管理功能。

## 🚀 快速开始

### 一键启动开发环境
```bash
./start-dev.sh
```

### 一键停止开发环境
```bash
./stop-dev.sh
```

## 📁 项目结构

```
Jcourse-stable/
├── jcourse-master/              # 前端项目 (Next.js)
├── jcourse_api-master/          # 后端项目 (Django)
├── 课表数据/                    # 课表CSV文件
├── 开发部署文档.md              # 详细部署文档
├── start-dev.sh                 # 启动脚本
├── stop-dev.sh                  # 停止脚本
└── README.md                    # 本文件
```

## 🛠️ 技术栈

**后端:**
- Django 4.2.16
- PostgreSQL 13
- Redis
- Django REST Framework

**前端:**
- Next.js
- React
- TypeScript

**部署:**
- Docker (数据库服务)
- Python 3.9+
- Node.js

## 📊 数据概览

系统已导入完整的课表数据：

- **总课程数**: 3,362门
- **总教师数**: 1,956名  
- **总院系数**: 30个
- **覆盖学期**: 3个学期

### 各学期课程分布
- 2025-2026-1: 1,476门课程
- 2024-2025-2: 1,268门课程  
- 2024-2025-1: 618门课程

## 🌐 访问地址

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **管理后台**: http://localhost:8000/admin (admin/admin123)

## 📖 详细文档

查看 [开发部署文档.md](./开发部署文档.md) 了解：
- 完整的环境搭建步骤
- 数据导入过程
- 常见问题解决方案
- 开发建议

## 🔧 手动操作

如果需要手动操作，可以参考以下命令：

### 启动数据库
```bash
cd jcourse_api-master
docker-compose -f docker-compose.dev.yml up -d
```

### 启动后端
```bash
cd jcourse_api-master
python3 manage.py runserver 0.0.0.0:8000
```

### 启动前端
```bash
cd jcourse-master
npm run dev
```

## 📝 开发注意事项

1. **环境要求**: Python 3.9+, Node.js, Docker
2. **数据库**: 使用Docker运行PostgreSQL和Redis
3. **认证**: 所有API端点都需要身份认证
4. **兼容性**: 已修复Python 3.9类型注解兼容性问题

## 🐛 故障排除

### Docker相关
- 确保Docker Desktop已启动
- 检查端口5432和6379是否被占用

### Python相关  
- 确认Python版本为3.9+
- 检查虚拟环境是否正确激活

### Node.js相关
- 使用`--legacy-peer-deps`解决依赖冲突
- 确认Node.js版本兼容性

## 📞 支持

如遇问题，请查看：
1. 控制台错误信息
2. 日志文件 (backend.log, frontend.log)
3. [开发部署文档.md](./开发部署文档.md) 中的常见问题部分

---

*最后更新: 2025-07-13*
