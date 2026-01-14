# CD AI Backend

Class Design AI 后端API服务

## 技术栈

- **Web框架**: FastAPI ≥0.123.9 (异步支持，自动生成 OpenAPI 文档)
- **Python版本**: 3.9+
- **数据库**: MySQL 8.0+ (使用 InnoDB 引擎，支持事务)
- **数据验证**: Pydantic ≥2.12.5 (请求/响应模型定义，强类型校验)
- **认证**: PyJWT ≥2.9.0 (生成/解析 JWT Token，HS256 算法)
- **密码加密**: bcrypt ≥4.2.0 (用户密码哈希存储)
- **HTTP客户端**: requests ≥2.32.0 (同步调用外部 AI 服务)
- **配置管理**: pydantic-settings (通过 BaseSettings 从 .env 加载配置)
- **ASGI服务器**: uvicorn ≥0.38.0 (开发与生产部署运行器)
- **文件上传**: python-multipart ≥0.0.20 (支持 FastAPI 的 UploadFile)
- **图像处理**: Pillow ≥12.0.0 (图表预览等扩展功能)

## 项目结构

```
CD_AI_back_end/
├── main.py                  # 应用入口 (FastAPI app instance)
├── app/
│   ├── __init__.py
│   ├── config.py            # 配置文件
│   ├── database.py          # 数据库连接
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   └── v1/              # API版本1
│   │       ├── __init__.py
│   │       ├── endpoints/   # 端点
│   │       └── routes.py    # 路由汇总
│   ├── core/                # 核心功能
│   │   ├── __init__.py
│   │   ├── security.py      # 安全相关
│   │   └── dependencies.py  # 依赖注入
│   ├── models/              # 数据模型
│   │   └── __init__.py
│   ├── schemas/             # Pydantic模式
│   │   └── __init__.py
│   ├── services/            # 业务逻辑
│   │   └── __init__.py
│   ├── middleware/          # 中间件
│   │   └── __init__.py
│   └── utils/               # 工具函数
│       └── __init__.py
├── alembic/                 # 数据库迁移
├── tests/                   # 测试
├── .env.example            # 环境变量示例
├── requirements.txt        # Python依赖
└── README.md              # 项目说明
```

## 快速开始

### 1. 创建虚拟环境

```bash
# 安装uv

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux and macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

#初始化环境
uv venv
```

### 2. 安装依赖

```bash
uv sync
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置。也可在类 Unix 系统上运行下面的命令快速复制：

```bash
cat .env.example > .env
```

在 PowerShell（Windows）中等价的命令为：

```powershell
Get-Content .env.example | Set-Content .env
```

### 4. 运行应用

```bash
# 快速运行
uv run main.py

# 开发模式
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. 访问API文档

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## 开发规范

- 使用类型提示 (Type Hints)
- 遵循PEP 8代码规范
- 编写单元测试
- 使用Alembic进行数据库迁移
