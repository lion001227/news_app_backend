# news_app_backend

基于 **FastAPI** 的新闻应用后端 API，提供新闻浏览、用户注册/登录、收藏与浏览历史管理等功能，使用 MySQL 作为主数据库，Redis 作为缓存。

## 技术栈

| 组件 | 用途 |
|------|------|
| FastAPI | Web 框架 / API 路由 |
| Uvicorn | ASGI 服务器 |
| Pydantic v2 | 数据验证与序列化 |
| SQLAlchemy 2.0 | ORM（异步） |
| aiomysql | MySQL 异步驱动 |
| Redis | 缓存（分类、新闻列表、详情） |
| passlib + bcrypt | 密码加密 |

## 目录结构

```
news_app_backend/
├── main.py                 # 应用入口，CORS 与路由挂载
├── requirements.txt        # Python 依赖
├── README.md               # 本说明文档
├── config/
│   ├── db_conf.py          # MySQL 异步引擎与会话（get_db 依赖）
│   └── cache_conf.py       # Redis 客户端与缓存读写封装
├── routers/                # 路由层
│   ├── news.py             # /api/news  (分类、列表、详情)
│   ├── users.py            # /api/user    (注册、登录、信息、修改密码)
│   ├── favorite.py         # /api/favorite (收藏增删查)
│   └── history.py          # /api/history (浏览历史增删查)
├── crud/                   # 数据访问层
│   ├── users.py
│   ├── news.py
│   ├── favorite.py
│   └── history.py
├── models/                 # SQLAlchemy ORM 模型
│   ├── users.py            # User, UserToken
│   ├── news.py             # Category, News
│   ├── favorite.py         # Favorite
│   └── history.py          # History
├── schemas/                # Pydantic 请求/响应模型
│   ├── users.py
│   ├── news.py
│   ├── favorite.py
│   └── history.py
├── cache/                  # 缓存业务封装
│   └── news.py
└── utils/                  # 工具类
    ├── response.py         # 统一成功响应
    ├── exception.py        # 全局异常处理器
    ├── exceptin_handlers.py# 异常处理器注册
    ├── security.py         # bcrypt 密码工具
    └── auth.py             # 基于 Token 的鉴权依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备服务

- **MySQL**：创建数据库 `news_app`，并按照 `models/` 中的 ORM 模型创建对应表（`user`、`user_token`、`news_category`、`news`、`favorite`、`history`）。
- **Redis**：本地运行 Redis，默认监听 `localhost:6379`，数据库索引 `0`。

### 3. 修改连接信息（如需要）

编辑以下文件中的连接参数：

- `config/db_conf.py` — `ASYNC_DB_URL`（MySQL 连接串，默认 `mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8`）
- `config/cache_conf.py` — `REDIS_HOST`、`REDIS_PORT`、`REDIS_DB`

### 4. 启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问自动文档：`http://127.0.0.1:8000/docs`

## API 接口

所有接口返回统一格式：
```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

### 新闻 (`/api/news`)

| 接口 | 方法 | 说明 | 参数 |
|------|------|------|------|
| `/categories` | GET | 获取新闻分类 | `offset`, `limit` |
| `/list` | GET | 获取新闻列表（分页） | `categoryId`, `page`, `pageSize` |
| `/detail` | GET | 新闻详情 | `id` |

### 用户 (`/api/user`)

| 接口 | 方法 | 说明 | 鉴权 |
|------|------|------|------|
| `/register` | POST | 用户注册 | 否 |
| `/login` | POST | 用户登录，返回 token | 否 |
| `/info` | GET | 获取当前用户信息 | 是 |
| `/update` | PUT | 更新用户信息 | 是 |
| `/password` | PUT | 修改密码 | 是 |

### 收藏 (`/api/favorite`)

| 接口 | 方法 | 说明 | 鉴权 |
|------|------|------|------|
| `/check` | GET | 检查新闻是否已收藏 | 是 |
| `/add` | POST | 添加收藏 | 是 |
| `/remove` | DELETE | 取消收藏 | 是 |
| `/list` | GET | 收藏列表（分页） | 是 |
| `/clear` | DELETE | 清空收藏 | 是 |

### 浏览历史 (`/api/history`)

| 接口 | 方法 | 说明 | 鉴权 |
|------|------|------|------|
| `/add` | POST | 添加浏览历史 | 是 |
| `/list` | GET | 浏览历史列表（分页） | 是 |
| `/delete/{news_id}` | DELETE | 删除单条历史 | 是 |
| `/clear` | DELETE | 清空历史 | 是 |

### 鉴权

需鉴权的接口在请求头中携带：

```
Authorization: Bearer <token>
```

Token 由登录/注册接口返回，有效期默认 7 天，存储于 `user_token` 表中。

## 数据库表

- `user`：用户基本信息
- `user_token`：用户登录凭证（token + 过期时间）
- `news_category`：新闻分类
- `news`：新闻正文
- `favorite`：用户收藏（用户+新闻唯一）
- `history`：用户浏览历史（浏览时间）

## 注意事项

- 代码中使用了 SQLAlchemy 2.0 异步风格（`AsyncSession`、`create_async_engine`），请确保 `aiomysql` 已安装。
- Redis 缓存不可用时不会阻断主流程，`cache/news.py` 读写失败会打印日志并返回空，降级到直接查数据库。
- 密码使用 bcrypt 加密存储，登录时通过 `passlib` 校验。
