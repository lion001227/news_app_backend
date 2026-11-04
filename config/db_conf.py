from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

ASYNC_DB_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8"

#创建异步引擎
async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=True,      #sql日志
    pool_size=10,   #连接池中保持的持久连接数
    max_overflow=20 #连接池允许创建的额外连接数
 )

#创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,   #数据库引擎
    class_=AsyncSession, #指定会话类
    expire_on_commit=False, #会话对象不过期，不重新查询数据库
)

#依赖项，用于获取数据库对话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()