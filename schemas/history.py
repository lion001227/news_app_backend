from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.news import NewsItemBase


class NewsId(BaseModel):
    news_id:int=Field(alias="newsId")

class History(NewsItemBase):
    view_time:datetime=Field(alias="viewTime")

class HistoryList(BaseModel):
    list:list[History]
    total:int
    has_more:bool=Field(alias="hasMore")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
