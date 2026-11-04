from fastapi import Header, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud.users import get_current_active_user


async def get_current_user(
        authorization:str=Header(...,alias="Authorization"),
        db:AsyncSession=Depends(get_db)
):
    # print("authorization =", repr(authorization))
    #前端的认证格式为Bearer xxxxxxxxxxxx，有两种写法
    #token=authorization.replace("Bearer","")/token=authorization.split(" ")[1],这里前端直接传了token值，所以直接取
    token=authorization.split(" ",1)[-1].strip()
    user=await get_current_active_user(token,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="令牌不存在或令牌已过期")
    return user