from fastapi import APIRouter, Query,HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import news

router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/categories")
async def get_categories(db:AsyncSession=Depends(get_db),offset: int = 0, limit: int = 100):
    categories=await news.get_categories(db,offset,limit)
    return {
        "code": 200,
        "message": "success",
        "data":categories,
            }

@router.get("/list")
async def get_list(
                   category_id: int=Query(...,alias="categoryId"),
                   page: int = 1,
                   pagesize:int=Query(10,le=100,alias="pageSize"),
                   db:AsyncSession=Depends(get_db),):
    news_list=await news.get_list(category_id,page,pagesize,db)
    news_total=await news.get_news_count(category_id,db)

    #跳过的条数+当前列表的条数<类别总条数news_total则可以翻页
    has_more=(page-1)*pagesize+len(news_list)<news_total

    return {
        "code": 200,
        "message": "success",
        "data":{
            "list":news_list,
            "total":news_total,
            "hasMore":has_more,
        }
    }

@router.get("/detail")
async def get_news_detail(news_id:int=Query(...,alias="id"),db:AsyncSession=Depends(get_db)):
    news_detail=await news.get_news_detail(news_id,db)
    if not news_detail:
        raise HTTPException(status_code=404,detail="新闻不存在")
    views_result=await news.increase_news_views(news_id,db)
    if not views_result:
        raise HTTPException(status_code=404,detail="新闻不存在")

    news_related=await news.get_news_related(news_id,news_detail.category_id,db)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": news_related
    }
    }