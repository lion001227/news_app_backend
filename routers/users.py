from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import users
from starlette import status

from models.users import User
from schemas.users import UserAuthResponse, UserInfoResponse,UserUpdateRequest,PasswordUpdateRequest
from utils.response import success_response
from utils import auth

router = APIRouter(prefix="/api/user",tags=["users"])

@router.post("/register")
async def register(user_data:users.UserData,db:AsyncSession=Depends(get_db)):
    user_exists = await users.get_user_by_username(user_data.username,db)
    if user_exists:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="用户已存在")

    new_user=await users.create_user(user_data,db)
    user_token=await users.create_token(new_user.id,db)

    # return {
    #   "code": 200,
    #   "message": "注册成功",
    #   "data": {
    #     "token": user_token,
    #     "userInfo": {
    #       "id": new_user.id,
    #       "username": new_user.username,
    #       "bio": new_user.bio,
    #       "avatar":new_user.avatar,
    #     }
    #   }
    # }
    response_data=UserAuthResponse(token=user_token,user_info=UserInfoResponse.model_validate(new_user))
    return success_response(message="注册成功",data=response_data)

@router.post("/login")
async def login(user_data:users.UserData,db:AsyncSession=Depends(get_db)):
    user = await users.authenticate_user(user_data.username,user_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="用户名或密码错误")
    user_token=await users.create_token(user.id,db)
    response_data=UserAuthResponse(token=user_token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功",data=response_data)

@router.get("/info")
async def get_user_info(user:User=Depends(auth.get_current_user)):
    return success_response(message="success",data=UserInfoResponse.model_validate(user))

@router.put("/update")
async def update_user_info(update_data:UserUpdateRequest,user:User=Depends(auth.get_current_user),db:AsyncSession=Depends(get_db)):
    user=await users.update_user_info(update_data,user.username,db)
    return success_response(message="更新成功",data=UserInfoResponse.model_validate(user))

@router.put("/password")
async def update_password(password:PasswordUpdateRequest,user:User=Depends(auth.get_current_user),db:AsyncSession=Depends(get_db)):
    result = await users.update_password(user,password,db)
    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="修改密码失败")
    if password.oldpassword==password.newpassword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="新旧密码不能相同")
    return success_response(message="密码修改成功")