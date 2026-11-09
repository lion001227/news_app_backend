import json

from fastapi import Query
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news import get_news_categories, set_news_categories, get_news_list_cache, set_news_list_cache,get_cache_news_detail,set_cache_news_detail
from config.db_conf import get_db
from models import news
from sqlalchemy import select, func, update

from models.news import News
from schemas.news import NewsItemBase


async def get_categories(db:AsyncSession=Depends(get_db),offset: int = 0, limit: int = 100):
    #获取缓存的新闻类别
    categories_cache=await get_news_categories()

    if categories_cache:
        print("获取缓存的新闻类别")
        return categories_cache

    #缓存获取不到的话找数据库里的
    print("获取数据库的新闻类别")
    result=await db.execute(select(news.Category).offset(offset).limit(limit))
    categories= result.scalars().all()

    #写入缓存表
    if categories:
        #将orm对象转换成json
        categories=jsonable_encoder(categories)
        print("将新闻类别写入缓存")
        await set_news_categories(categories)

    return categories



async def get_list(category_id: int=Query(...,alias="categoryId"),
                   page: int = 1,
                   pagesize:int=Query(10,le=100,alias="pageSize"),
                   db:AsyncSession=Depends(get_db),):
    #从缓存里读取新闻列表
    #获取页码page=(num-1)*pagesize-->num=page//pagesize+1
    num = page // pagesize + 1
    news_list=await get_news_list_cache(category_id,num,pagesize)
    if news_list:
        #转成orm
        return [News(**item) for item in news_list]

    #获取新闻列表
    result=await db.execute(select(news.News).where(News.category_id==category_id).offset((page-1)*pagesize).limit(pagesize))
    news_list=result.scalars().all()
    if news_list:
        #将orm数据转换成字典再写入缓存
        #orm转成pydantic再转字典，model_validate-->pydantic，model_dump-->dict
        #by_alias=False，不用别名，Redis给后端用的
        value=[NewsItemBase.model_validate(item).model_dump(mode="json",by_alias=False) for item in news_list]
        await set_news_list_cache(category_id,num,pagesize,value)
    return news_list

async def get_news_count(category_id: int,db:AsyncSession=Depends(get_db)):
    #获取一个类别下的新闻总条数
    result=await db.execute(select(func.count(News.id)).where(News.category_id==category_id))
    return result.scalar_one()

async def get_news_detail(news_id: int,db:AsyncSession=Depends(get_db)):
    #查询缓存中的新闻详情
    detail=await get_cache_news_detail(news_id)
    if detail:
        return detail
    #获取新闻细节
    result=await db.execute(select(News).where(News.id==news_id))
    detail=result.scalar_one_or_none()
    #将新闻详情写入缓存
    if detail:
        data=jsonable_encoder(detail)
        await set_cache_news_detail(news_id,data)
    return detail

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