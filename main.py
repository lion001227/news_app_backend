from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from utils.exceptin_handlers import register_exception_handler
from routers import news,users

app = FastAPI()

#异常处理
register_exception_handler(app)

# 允许的源
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
]

#添加cors中间件,解决异域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    #允许访问的源
    allow_credentials=True,   #允许携带Cookie
    allow_methods=["*"],      #允许所有请求方法
    allow_headers=["*"],      #允许所有请求头
)

#挂载路由
app.include_router(news.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


