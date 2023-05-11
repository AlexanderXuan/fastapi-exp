'''
Author: AlexanderXuan xuanxiaoguang@gmail.com
Date: 2023-05-07 19:54:09
LastEditors: AlexXuan xuanxiaoguang@gmail.com
LastEditTime: 2023-05-11 08:47:24
FilePath: /fastapi-exp/tutorial/chapter05.py
'''
from typing import Optional, List, Union
from fastapi import APIRouter, Depends, Header, HTTPException

app05 = APIRouter()

"""Dependencies 创建、导入和声明依赖"""
async def common_parameters(q: Optional[str] = None, page: int = 1, limit: int = 10):
    return {"q": q, "page": page, "limit": limit}

@app05.get("/dependencies01")
async def dependencies01(commons: dict = Depends(common_parameters)):
    return commons

@app05.get("/dependencies02")
def dependencies02(commons: dict = Depends(common_parameters)):
    return commons


"""Classes as Dependencies 类作为依赖项"""
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, page: int = 1, limit: int = 10):
        self.q = q
        self.page = page
        self.limit = limit


@app05.get("/classes_as_dependencies")
# async def classes_as_dependencies(commons: CommonQueryParams = Depends(CommonQueryParams)):
# async def classes_as_dependencies(commons: CommonQueryParams = Depends()):
async def classes_as_dependencies(commons=Depends(CommonQueryParams)):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.page : commons.page + commons.limit]
    response.update({"items": items})
    return response


"""Sub-dependencies 子依赖"""
def query(q: Optional[str] = None):
    pass    # do some public process
    return q

def sub_query(q: str = Depends(query), last_query: Optional[str] = None):
    if not q:
        return last_query
    return q

@app05.get("/sub_dependencies")
async def sub_dependencies(final_query: str = Depends(sub_query, use_cache=True)):
    """use_cache: 默认为True，表示当多个依赖有一个共同的子依赖时，每次request请求只会调用子依赖一次，多次调用会使用缓存的结果"""
    return {"sub_dependencies": final_query}


"""Dependencies in path operations decorators 路径操作装饰器中的依赖项"""
async def verify_token(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")
    return x_token

async def verify_key(x_key: str = Header(...)):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-key header invalid")
    return x_key

@app05.get("/dependencies_in_path_operations_decorators", dependencies=[Depends(verify_token), Depends(verify_key)])
async def dependencies_in_path_operations_decorators():
    return [{"user": "user01"}, {"user": "user02"}]