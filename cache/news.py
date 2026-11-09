#缓存：key-value
from typing import List, Dict, Any, Optional

from config.cache_conf import get_json_cache, set_cache

#Redis 风格命名空间
CATEGORIES_KEY="news:categories"
NEWS_KEY_PREFIX="news:list"
DETAIL_KEY_PREFIX="news:detail"

#获取新闻分类缓存
async def get_news_categories():
    return await get_json_cache(CATEGORIES_KEY)

#写入新闻分类缓存
#分类、配置：7200s，列表：600，详情：1800，验证码：120，数据越稳定的，设置的缓存时间越长
async def set_news_categories(value:List[Dict[str, Any]],expire:int=7200):
    return await set_cache(CATEGORIES_KEY,value,expire)


#获取新闻列表
async def get_news_list_cache(category:Optional[int],page:int,page_size:int):
    category=category if category is not None else "all"
    key=f"{NEWS_KEY_PREFIX}{category}:{page}:{page_size}"
    return await get_json_cache(key)

#写入新闻列表缓存
async def set_news_list_cache(category:Optional[int],page:int,page_size:int,value,expire:int=1800):
    category=category if category is not None else "all"
    key=f"{NEWS_KEY_PREFIX}{category}:{page}:{page_size}"
    return await set_cache(key,value,expire)

#获取新闻详情缓存
async def get_cache_news_detail(news_id:int):
    return await get_json_cache(f"{NEWS_KEY_PREFIX}{news_id}")

#写入新闻详情缓存
async def set_cache_news_detail(news_id:int,value:str,expire:int=600):
    await set_cache(f"{DETAIL_KEY_PREFIX}:{news_id}",value,expire)