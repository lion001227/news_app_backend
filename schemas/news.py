from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class NewsItemBase(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image:Optional[str]=None
    author:Optional[str]=None
    category_id: int=Field(alias="categoryId")
    views:int
    publish_time:Optional[datetime]=Field(None,alias="publishTime")

    model_config = ConfigDict(
        from_attributes=True,#支持从对象属性读取数据
        populate_by_name=True#允许用字段名或别名传参
    )