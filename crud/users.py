import uuid
from datetime import timedelta, datetime

from fastapi import Depends, HTTPException
from sqlalchemy import select, update

from models.users import User, UserToken
from schemas.users import UserData, UserUpdateRequest, PasswordUpdateRequest
from utils.security import get_password_hash,verify_password


async def get_user_by_username(username:str,db):
    #查询用户是否存在
    result=await db.execute(select(User).where(User.username==username))
    return result.scalars().one_or_none()

async def create_user(user_data:UserData,db):
    #创建新用户
    hashed_password = get_password_hash(user_data.password)
    user=User(username=user_data.username,password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)  #从数据库读回最新的user
    return user

async def create_token(user_id,db):
    #获取token
    token=str(uuid.uuid4())
    #设置过期时间为7天1小时30分钟30秒后,timedelta(days=7,hours=1,minutes=30,seconds=30)
    expires_at=datetime.now()+timedelta(days=7)
    #检查token是否存在
    query=await db.execute(select(UserToken).where(UserToken.user_id==user_id))
    user_token=query.scalars().one_or_none()

    if not user_token:
        user_token=UserToken(token=token,user_id=user_id,expires_at=expires_at)
        db.add(user_token)
    else:
        user_token.token=token
        user_token.expires_at=expires_at
    await db.commit()
    return token

async def authenticate_user(username:str,password:str,db):
    #用户登录校验
    user=await get_user_by_username(username,db)
    if not user:
        return None
    if not verify_password(password,user.password):
        return None

    return user

async def get_current_active_user(token:str,db):

    query=await db.execute(select(UserToken).where(UserToken.token==token))
    user_token=query.scalars().one_or_none()
    #检验令牌是否存在是否过期
    if not user_token or user_token.expires_at < datetime.now():
        return None
    user=await db.execute(select(User).where(User.id==user_token.user_id))
    return user.scalars().one_or_none()

async def update_user_info(userdata:UserUpdateRequest,username:str,db):
    #model_dump把pydantic模型转换成字典，**解包字典，从"A":"B"->  A=B
    result=await db.execute(update(User).where(User.username == username).values(**userdata.model_dump(
        exclude_none=True,      #排除未设置的字段
        exclude_unset=True      #排除值为 None 的字段
    )))
    await db.commit()

    if  result.rowcount==0:
        raise HTTPException(status_code=404,detail="用户不存在")

    update_user=await get_user_by_username(username,db)
    return update_user

async def update_password(user:User,password:PasswordUpdateRequest,db):
    #验证旧密码->设置新密码、加密->提交数据库
    print(f"用户旧密码：{user.password}\n password.oldpassword:{password.oldpassword}")
    if not verify_password(password.oldpassword,user.password):
        return False

    hashed_password=get_password_hash(password.newpassword)
    user.password=hashed_password
    #确保能提交到数据库
    db.add(user)
    await db.commit()

    return True

