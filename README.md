# JCourse评课社区

西南财经大学课程评价社区系统

## 项目简介

JCourse是一个基于Django + Next.js的课程评价社区系统，为学生提供课程评价、查看和分享的平台。

## 技术栈

- **后端**: Django 4.2.16 + Django REST Framework
- **前端**: Next.js 13.5.4 + TypeScript + Ant Design
- **数据库**: PostgreSQL
- **缓存**: Redis
- **部署**: Docker + Docker Compose

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 24.3.0+
- Docker & Docker Compose
- Git

### 本地部署

```bash
# 克隆项目
git clone https://github.com/harry51888/jcourse-swufe.git
cd jcourse-swufe

# 执行部署脚本
chmod +x deploy-local.sh
./deploy-local.sh
```

### 访问地址

- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- 管理后台: http://localhost:8000/admin (admin/admin123)

## 功能特性

- ✅ 课程搜索和筛选
- ✅ 课程评价和评分
- ✅ 用户认证和权限管理
- ✅ 管理后台
- ✅ 响应式设计
- ✅ 全文搜索
- ✅ 评价数据独立显示

## 数据统计

- 课程数据: 3,362门课程
- 评价数据: 894条独立评价记录
- 教师数据: 1,956名教师
- 院系数据: 30个院系

## 项目结构

```
jcourse-swufe/
├── jcourse_api-master/     # Django后端
├── jcourse-master/         # Next.js前端
├── jcourse-data/          # 数据文件
├── deploy-local.sh        # 本地部署脚本
├── 部署经验总结.md        # 详细部署文档
└── README.md             # 项目说明
```

## 部署说明

详细的部署步骤和问题解决方案请参考：[部署经验总结.md](./部署经验总结.md)

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 许可证

MIT License

## 联系方式

- GitHub: https://github.com/harry51888/jcourse-swufe
- Issues: https://github.com/harry51888/jcourse-swufe/issues
