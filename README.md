# NCRE-Review-System

全国计算机等级考试（NCRE）复习平台，采用前后端分离架构，适合作为课程设计、比赛展示和个人作品集项目。

当前版本已经支持：

- 多用户注册与登录
- 用户数据隔离
- 科目选择、章节大纲、练习、模拟考试
- 错题本、收藏、学习统计
- 本地 SQLite 题库与种子数据

## 技术栈

后端：

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

前端：

- Vue 3
- Vite
- TypeScript
- Element Plus
- ECharts
- Pinia
- Axios

## 当前内置科目

- 一级：人工智能与大模型基础
- 二级：WPS Office 高级应用与设计
- 二级：MS Office 高级应用与设计
- 三级：数据库技术

## 项目结构

```text
NCRE-Review-System/
├─ README.md
├─ backend/
│  ├─ .env
│  ├─ requirements.txt
│  ├─ ncre_review.db
│  ├─ app/
│  ├─ scripts/
│  └─ tests/
├─ frontend/
│  ├─ package.json
│  ├─ vite.config.ts
│  └─ src/
└─ docs/
```

## 数据库核心表

- `users`
- `auth_tokens`
- `subjects`
- `chapters`
- `questions`
- `study_records`
- `wrong_questions`
- `favorite_questions`
- `mock_exams`
- `mock_exam_answers`

## 种子数据说明

当前种子脚本只初始化题库基础数据，不再自动创建任何演示账号。

初始化后将包含：

- 4 个科目
- 24 个章节
- 120 道题目

不会包含：

- 默认用户
- 默认错题记录
- 默认模拟考试成绩

首次使用请先注册账号。

## 安装依赖

### 后端

```powershell
cd C:\Users\deng\Documents\Playground\NCRE-Review-System\backend
& "C:\Users\deng\AppData\Local\Programs\Python\Python310\python.exe" -m pip install -r requirements.txt
```

### 前端

```powershell
cd C:\Users\deng\Documents\Playground\NCRE-Review-System\frontend
npm install
```

## 初始化数据库

```powershell
cd C:\Users\deng\Documents\Playground\NCRE-Review-System\backend
& "C:\Users\deng\AppData\Local\Programs\Python\Python310\python.exe" scripts/seed_data.py
```

## 启动方式

### 启动后端

```powershell
cd C:\Users\deng\Documents\Playground\NCRE-Review-System\backend
& "C:\Users\deng\AppData\Local\Programs\Python\Python310\python.exe" -m uvicorn app.main:app --reload
```

后端访问地址：

- 服务地址：[http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger 文档：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 启动前端

```powershell
cd C:\Users\deng\Documents\Playground\NCRE-Review-System\frontend
npm run dev
```

前端访问地址：

- 登录页：[http://127.0.0.1:5173/login](http://127.0.0.1:5173/login)
- 项目首页：[http://127.0.0.1:5173](http://127.0.0.1:5173)

## 部署

如果你想把项目部署到云服务器，让其他人从自己的电脑访问，请看：

- [DEPLOYMENT.md](C:\Users\deng\Documents\Playground\NCRE-Review-System\DEPLOYMENT.md)

项目已经补好：

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `frontend/nginx/default.conf`
- `docker-compose.prod.yml`

## 环境变量

后端 `.env` 示例：

```env
APP_NAME=NCRE Review System API
APP_ENV=development
API_V1_PREFIX=/api/v1
SQLITE_DB_PATH=./ncre_review.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## 已实现页面

- 登录/注册页
- 首页 Dashboard
- 科目列表页
- 科目详情页
- 练习中心
- 模拟考试页
- 成绩分析页
- 错题本页
- 学习统计页

## 已实现接口

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`
- `GET /api/v1/subjects`
- `GET /api/v1/subjects/{id}`
- `GET /api/v1/chapters`
- `GET /api/v1/questions`
- `GET /api/v1/questions/random`
- `POST /api/v1/practice/submit`
- `POST /api/v1/mock-exams/generate`
- `POST /api/v1/mock-exams/{id}/submit`
- `GET /api/v1/statistics/overview`
- `GET /api/v1/wrong-questions`
- `POST /api/v1/favorites`
- `DELETE /api/v1/favorites/{question_id}`

## 多用户说明

项目当前已支持注册登录。每个用户拥有独立的：

- 学习记录
- 错题本
- 收藏题目
- 模拟考试记录
- 统计分析数据

初始化后系统不会再预置任何演示账号。

## 后续升级路线

- JWT 正式化与刷新令牌
- 用户资料页
- 班级/教师/管理员角色
- 真题批量导入
- AI 智能出题
- 错题推荐与学习计划
- 管理后台
- PostgreSQL 部署版
