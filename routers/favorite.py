from fastapi import APIRouter, Query, HTTPException
from fastapi.params import Depends
from pyexpat.errors import messages
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from models.users import User
from schemas.favorite import CheckNewsFavorite, AddFavorite, FavoriteNewsList
from utils.auth import get_current_user
from utils.response import success_response
from crud import favorite

router = APIRouter(prefix="/api/favorite",tags=["favorite"])

@router.get("/check")
async def check_favorite_status(new_id:int=Query(...,alias="newsId"),
                                user:User=Depends(get_current_user),
                                db:AsyncSession=Depends(get_db)):
    result=await favorite.check_favorite_news(user.id,new_id,db)
    return success_response(message="success",data=CheckNewsFavorite(isFavorite=result))

@router.post("/add")
async def add_favorite_news(data:AddFavorite,user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    favorite_news = await favorite.add_favorite(user.id,data.news_id,db)
    return success_response(message="收藏成功",data=favorite_news)

@router.delete("/remove")
async def delete_favorite_news(news_id:int=Query(...,alias="newsId"),user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    result=await favorite.delete_favorite(user.id,news_id,db)
    if not result:
        raise HTTPException(status_code=404,detail="收藏记录不存在")
    return success_response(message="取消收藏成功")

@router.get("/list")
async def get_favorite_news_list(page:int=Query(1,ge=1),
                                 page_size:int=Query(10,ge=1,le=100,alias="pageSize"),
                                 user:User=Depends(get_current_user),
                                 db:AsyncSession=Depends(get_db)):
    rows,total=await favorite.get_favorite_list(db,user.id,page,page_size)

    favorite_list=[{
        **news.__dict__,
        "favorite_time":favorite_time,
        "favorite_id":favorite_id
    } for news,favorite_time,favorite_id in rows]

    has_more=total-page*page_size>0

    data=FavoriteNewsList(list=favorite_list,total=total,hasMore=has_more)
    return success_response(message="success",data=data)

@router.delete("/clear")
async def clear_favorite_news_list(user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    count = await favorite.clear_favorite_news(user.id,db)
    return success_response(message=f"成功删除{count}条记录")