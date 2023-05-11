'''
Author: AlexanderXuan xuanxiaoguang@gmail.com
Date: 2023-05-07 19:53:37
LastEditors: AlexXuan xuanxiaoguang@gmail.com
LastEditTime: 2023-05-11 08:20:47
FilePath: /fastapi-exp/run.py
'''
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from tutorial import app03, app04, app05

# from fastapi.exceptions import RequestValidationError
# from fastapi.responses import PlainTextResponse
# from fastapi.exceptions import HTTPException
# from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(
    title="FastAPI Tutorial and Coronavirus Tracker API Docs",
    description="FastAPI教程 新冠病毒跟踪器API接口文档",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redocs",
)

# mount表示将某个目录下一个完全独立的应用挂在过来，这个不会在API交互文档中显示
app.mount(path='/staticstatic', app=StaticFiles(directory='./coronavirus/static'), name='static') # 静态文件不要挂载到APIRouter中

# @app.exception_handler(StarletteHTTPException)  # 重写HTTPException异常处理
# async def http_exception_handler(request, exc):
#     return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

# @app.exception_handler(RequestValidationError)  # 重写请求验证异常处理
# async def validation_exception_handler(request, exc):
#     return PlainTextResponse(str(exc), status_code=400)


app.include_router(app03, prefix="/chapter03", tags=["第三章 请求参数和验证"])
app.include_router(app04, prefix="/chapter04", tags=["第四章 响应处理和FastAPI配置"])
app.include_router(app05, prefix="/chapter05", tags=["第五章 FastAPI依赖注入系统"])

if __name__ == "__main__":
    uvicorn.run('run:app', host="0.0.0.0", port=8000, reload=True, workers=1)

# /
# /coronavirus
# /tutorial

# 启动命令：python run.py