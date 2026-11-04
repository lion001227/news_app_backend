from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UserData(BaseModel):
    username: str
    password: str

#user_info对应的类：基础类（可为空的字段）+Info类（必填）
class UserInfoBase(BaseModel):
    #用户信息基础数据模型
    nickname: Optional[str] = Field(None,max_length=50,description="昵称")
    avatar: Optional[str] = Field(None,max_length=255,description="头像URL")
    gender: Optional[str] = Field(None,max_length=10,description="性别")
    bio: Optional[str]=Field(None,max_length=500,description="个人简介")

class UserInfoResponse(UserInfoBase):
    id: int
    username: str

    #模型配置类
    model_config=ConfigDict(from_attributes=True )#允许从ORM对象属性中取值

class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse=Field(...,alias="userInfo")

    #模型类配置
    model_config=ConfigDict(
        populate_by_name=True,   #alias/字段名兼容
        from_attributes=True )   #允许从ORM对象属性中取值

class UserUpdateRequest(BaseModel):
    nickname: str=Field(None,description="昵称")
    avatar: str=Field(None,description="头像URL")
    gender: str=Field(None,description="性别")
    bio: str=Field(None,description="个人简介")
    phone:str=Field(None,description="手机号")

class PasswordUpdateRequest(BaseModel):
    oldpassword: str=Field(...,alias="oldPassword")
    newpassword: str=Field(...,alias="newPassword")