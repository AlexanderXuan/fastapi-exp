'''
Author: AlexanderXuan xuanxiaoguang@gmail.com
Date: 2023-05-07 19:53:37
LastEditors: AlexanderXuan xuanxiaoguang@gmail.com
LastEditTime: 2023-05-07 20:03:00
FilePath: /fastspi-exp/run.py
'''
import uvicorn
from fastapi import FastAPI

from tutorial import app03, app04, app05

app = FastAPI()

app.include_router(app03, prefix="/chapter03", tags=["第三章 请求参数和验证"])
app.include_router(app04, prefix="/chapter04", tags=["第四章 响应处理和FastAPI配置"])
app.include_router(app05, prefix="/chapter05", tags=["第五章 FastAPI依赖注入系统"])

if __name__ == "__main__":
    uvicorn.run('run:app', host="0.0.0.0", port=8000, reload=True, workers=1)

# /
# /coronavirus
# /tutorial

# 启动命令：python run.py