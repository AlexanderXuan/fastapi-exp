'''
Author: AlexanderXuan xuanxiaoguang@gmail.com
Date: 2023-05-07 19:54:06
LastEditors: AlexanderXuan xuanxiaoguang@gmail.com
LastEditTime: 2023-05-07 21:26:51
FilePath: /fastspi-exp/tutorial/chapter04.py
'''
from typing import Optional, List, Union
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

app04 = APIRouter()

"""Response Model 响应模型"""
class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    mobile: str = "10086"
    address: str = None
    full_name: Optional[str] = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    mobile: str = "10086"
    address: str = None
    full_name: Optional[str] = None


users = {
    "user01": {
        "username": "user01",
        "password": "123456",
        "email": "user01@example.com",
    },
    "user02": { # 用于测试响应模型  
        "username": "user02",
        "password": "123456",
        "email": "user02@example.com",
        "mobile": "110",
    },
}

#path operation decorator
@app04.post("/response_model", response_model=UserOut, response_model_exclude_unset=True)
async def response_model(user: UserIn):
    """
    response_model_exclude_unset: 仅返回已设置的值
    """
    print(user.password)
    return users["user02"]

@app04.post(
    "/response_model/attributes", 
    response_model=UserOut,
    # response_model=Union[UserIn, UserOut]
    # response_model=List[UserOut]
    response_model_include=["username", "email", "mobile"],
    response_model_exclude=["mobile"],
)
async def response_model_attributes(user: UserIn):
    """include/exclude: 仅返回指定的字段"""
    # del user.password
    return user # [user, user] for List[UserOut]
