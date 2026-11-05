from idlelib.query import Query

from fastapi import HTTPException
from sqlalchemy import select, delete, func

from models.favorite import Favorite
from models.news import News


async def check_favorite_news(user_id,news_id,db):
    query=await db.execute(select(Favorite).where(Favorite.user_id==user_id,Favorite.news_id==news_id))
    result=query.scalar_one_or_none()

    return result is not None

async def add_favorite(user_id,news_id,db):
    favorite=Favorite(user_id=user_id,news_id=news_id)
    db.add(favorite)
    await db.commit()
    return favorite

async def delete_favorite(user_id,news_id,db):
    news=delete(Favorite).where(Favorite.user_id==user_id,Favorite.news_id==news_id)
    result=await db.execute(news)
    await db.commit()
    return result.rowcount>0

async def get_favorite_list(db,user_id,page:int=1,page_size:int=10):
    #返回总数，新闻列表
    total_query=await db.execute(select(func.count()).where(Favorite.user_id==user_id))
    total=total_query.scalar_one()

    #获取收藏列表，联表查询，按收藏时间排序，分页
    #select(查询的主体模型类,字段别名).join(联合查询的模型类，联合查询的条件)
    #rows返回的结果为[(新闻对象，收藏时间，收藏id)]
    list_query=((select(News,Favorite.created_at.label("favorite_time"),Favorite.id.label("favorite_id"))
                .join(Favorite,Favorite.news_id==News.id))
                .where(Favorite.user_id==user_id)
                .order_by(Favorite.created_at.desc())
                .offset(page_size*(page-1)).limit(page_size))

    query_list=await db.execute(list_query)
    rows=query_list.all()
    return rows,total

async def clear_favorite_news(user_id,db):
    result=await db.execute(delete(Favorite).where(Favorite.user_id==user_id))
    await db.commit()
    if result.rowcount<1:
        raise HTTPException(status_code=404, detail="没有收藏记录")
    return result.rowcount

