# Online Reading Plus System

一个基于FastAPI的在线阅读系统，支持用户管理、书籍阅读、支付充值等功能。
- 目录结构
- 配置管理
- 数据库（异步 + 分表）
- 缓存策略
- 权限控制
- 日志 & 监控
- 异常处理
- 中间件
- 测试 & CI/CD
- 部署方案
## 功能特性

- 用户注册登录与身份验证
- 书籍浏览与阅读
- 阅读历史记录
- 支付与充值功能
- 广告管理
- 管理员后台

## 技术栈

- **后端框架**: FastAPI (异步)
- **数据库**: MySQL (用户、支付等关系数据)
- **文档数据库**: MongoDB (书籍内容等非结构化数据)
- **缓存**: Redis
- **ORM**: SQLAlchemy (异步)
- **部署**: Docker + Docker Compose

## 项目结构

```
.
├── app/                    # 主应用目录
│   ├── main.py            # FastAPI实例入口
│   ├── config/            # 配置文件
│   ├── models/            # 数据库模型
│   ├── schemas/           # Pydantic模型
│   ├── api/               # API路由
│   ├── core/              # 核心业务逻辑
│   ├── utils/             # 工具函数
│   ├── middleware/        # 中间件
│   ├── templates/         # 模板文件
│   └── static/            # 静态文件
├── migrations/            # 数据库迁移文件
├── tests/                 # 测试文件
├── sensitiveWord/         # 敏感词库
├── .env                   # 环境变量
├── .gitignore             # Git忽略文件
├── requirements.txt       # 依赖包
├── run.py                 # 应用启动文件
├── Dockerfile             # Docker配置
└── docker-compose.yml     # Docker Compose配置
```

## 安装与运行

### 本地运行

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 配置环境变量：
   复制 `.env.example` 为 `.env` 并填写相应配置

3. 运行应用：
   ```bash
   python run.py
   ```

### Docker运行

```bash
docker-compose up -d
```

## 数据库迁移

使用Alembic进行数据库迁移：

```bash
# 初始化迁移
alembic init migrations

# 创建迁移脚本
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

## API文档

运行后访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc