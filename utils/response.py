from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse


def success_response(message:str="响应成功",data=None):
    content={
        "code":200,
        "message":message,
        "data":data}

    #把任何的fastapi，orm，pydantic对象正常响应成content的格式
    return JSONResponse(content=jsonable_encoder(content))