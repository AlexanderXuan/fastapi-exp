'''
Author: AlexanderXuan xuanxiaoguang@gmail.com
Date: 2023-05-07 19:54:07
LastEditors: AlexXuan xuanxiaoguang@gmail.com
LastEditTime: 2023-05-13 21:22:41
FilePath: /fastapi-exp/tutorial/chapter07.py
'''
from fastapi import APIRouter, Depends, Request

"""【见coronavirus应用】SQL (Relational) Databases FastAPI的数据库操作"""

"""Bigger Applications - Multiple Files 多应用的目录结构设计"""


async def get_user_agent(request: Request):
    print(request.headers["User-Agent"])


app07 = APIRouter(
    prefix="/bigger_applications",
    tags=["第七章 FastAPI的数据库操作和多应用的目录结构设计"],  # 与run.py中的tags名称相同
    dependencies=[Depends(get_user_agent)],
    responses={200: {"description": "Good job!"}},
)


@app07.get("/bigger_applications")
async def bigger_applications():
    return {"message": "Bigger Applications - Multiple Files"}
