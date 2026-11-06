from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from models.users import User
from schemas.history import NewsId, HistoryList
from utils.auth import get_current_user
from utils.response import success_response
from crud.history import add_history,get_history_news_list,delete_history_news,clear_history_news

router = APIRouter(prefix="/api/history",tags=["history"])

@router.post("/add")
async def get_history(news_id:NewsId,user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    history = await add_history(news_id.news_id,user.id,db)
    return success_response(message="添加成功",data=history)

@router.get("/list")
async def get_history_list(page:int=Query(1,ge=1),
                           page_size:int=Query(10,ge=1,le=100,alias="pageSize"),
                           user:User=Depends(get_current_user),
                           db:AsyncSession=Depends(get_db)):
    total,rows=await get_history_news_list(user.id,db,page_size,page)
    has_more=total-(page*page_size)>0
    history_list=[{**news.__dict__,
           "viewTime":viewTime}
          for news,viewTime in rows]
    data=HistoryList(list=history_list,total=total,hasMore=has_more)
    return success_response(message="success",data=data)

@router.delete("/delete/{news_id}")
async def delete_history(news_id:int,user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    result=await delete_history_news(news_id,user.id,db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="浏览记录不存在")
    return success_response(message="删除成功")

@router.delete("/clear")
async def clear_history(user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    result=await clear_history_news(user.id,db)
    if not result:
        raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="浏览记录不存在")
    return success_response(data="清空成功")