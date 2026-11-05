from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from schemas.news import NewsItemBase


class CheckNewsFavorite(BaseModel):
    is_favorite: bool=Field(...,alias="isFavorite")

class AddFavorite(BaseModel):
    news_id: int=Field(...,alias="newsId")

class FavoriteNews(NewsItemBase):
    favorite_id: int=Field(...,alias="favoriteId")
    favorite_time: datetime=Field(...,alias="favoriteTime")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

class FavoriteNewsList(BaseModel):
    list:list[FavoriteNews]
    total:int
    has_more: bool=Field(alias="hasMore")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


