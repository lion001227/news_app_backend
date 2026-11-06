from itertools import groupby

from click import group
from sqlalchemy import select, func, delete

from models.history import History
from models.news import News


async def add_history(news_id,user_id,db):
    history=History(news_id=news_id,user_id=user_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history

async def get_history_news_list(user_id,db,page_size:int=10,page:int=1):
    #给出总条数total还有数据列表data
    query=await db.execute(select(func.count()).where(History.user_id==user_id))
    total=query.scalar_one()

    query_list=await db.execute(((select(News,History.view_time.label("viewTime"))
     .join(History,History.news_id==News.id)
     .where(History.user_id==user_id)).order_by(History.view_time.desc())
     .offset((page-1)*page_size).limit(page_size)))

    data_list=query_list.all()
    # print(data_list[0])
    return total,data_list

async def delete_history_news(news_id,user_id,db):
    history=delete(History).where(History.news_id==news_id,History.user_id==user_id)
    result=await db.execute(history)
    await db.commit()
    return result.rowcount>0

async def clear_history_news(user_id,db):
    history=delete(History).where(History.user_id==user_id)
    result=await db.execute(history)
    await db.commit()
    return result.rowcount>0