from fastapi import Query
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from models import news
from sqlalchemy import select, func, update

from models.news import News


async def get_categories(db:AsyncSession=Depends(get_db),offset: int = 0, limit: int = 100):
    #获取新闻类别
    result=await db.execute(select(news.Category).offset(offset).limit(limit))
    return result.scalars().all()

async def get_list(category_id: int=Query(...,alias="categoryId"),
                   page: int = 1,
                   pagesize:int=Query(10,le=100,alias="pageSize"),
                   db:AsyncSession=Depends(get_db),):
    #获取新闻列表
    result=await db.execute(select(news.News).where(News.category_id==category_id).offset((page-1)*pagesize).limit(pagesize))
    return result.scalars().all()

async def get_news_count(category_id: int,db:AsyncSession=Depends(get_db)):
    #获取一个类别下的新闻总条数
    result=await db.execute(select(func.count(News.id)).where(News.category_id==category_id))
    return result.scalar_one()

async def get_news_detail(news_id: int,db:AsyncSession=Depends(get_db)):
    #获取新闻细节
    result=await db.execute(select(News).where(News.id==news_id))
    return result.scalar_one_or_none()

async def increase_news_views(news_id: int,db:AsyncSession=Depends(get_db)):
    #更新浏览量
    result=await db.execute(update(News).where(News.id==news_id).values(views=News.views+1))
    await db.commit()

    #检查是否成功更新到数据库
    return result.rowcount>0

async def get_news_related(news_id: int,category_id:int,db:AsyncSession=Depends(get_db),limit:int=5):
    result=await db.execute(select(News)
                            .where(News.category_id==category_id,News.id != news_id)
                            .order_by(News.views.desc(),#降序，默认为升序
                                      News.publish_time.desc(),)
                            .limit(limit))
    return [{"id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,} for news_detail in result.scalars().all()]