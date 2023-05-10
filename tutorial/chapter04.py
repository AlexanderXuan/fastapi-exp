'''
Author: AlexanderXuan xuanxiaoguang@gmail.com
Date: 2023-05-07 19:54:06
LastEditors: AlexXuan xuanxiaoguang@gmail.com
LastEditTime: 2023-05-10 08:57:47
FilePath: /fastapi-exp/tutorial/chapter04.py
'''
from typing import Optional, List, Union
from fastapi import APIRouter, status, Form, File, UploadFile
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


"""Response Status Code 响应状态码"""

@app04.post("/status_code", status_code=200)
async def status_code():
    return {"status_code": 200}

@app04.post("/status_attribute", status_code=status.HTTP_200_OK)
async def status_code():
    print(type(status.HTTP_200_OK))
    return {"status_code": status.HTTP_200_OK}


"""Form Data 表单数据处理"""

@app04.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):  # 定义表单参数
    """用Form类需要pip install python-multipart; 校验类似前面的请求参数验证, Form表单和body的差异在于请求头中的content-type有差异"""
    return {"username": username}

"""Request Files 单文件、多文件上传及参数详解"""

@app04.post("/file")
async def file_(file: bytes = File(...)):   # 上传多个文件变为file: List[bytes] = File(...)
    """使用File类 文件内容会以bytes形式读入内存 适合于上传小文件"""
    return {"file_size": len(file)}


@app04.post("/upload_files")
async def upload_files(files: List[UploadFile] = File(...)):    # 上传单个文件变为file: UploadFile = File(...)
    """使用UploadFile类的优势：
    1. 文件存储在内存中，使用的内存达到阈值后，将被保存在磁盘中；
    2. 适合于图片、视频大文件
    3. 可以获取上传文件的元数据，如文件名，创建时间等
    4. 有文件对象的异步接口（用异步方式读取或更改文件）
    5. 上传的文件时Python文件对象，可以使用write(), read(), seek(), close()操作
    """
    for file in files:
        contents = await file.read()
        print(contents)
    
    return {"filename": files[0].filename, "content_type": files[0].content_type}

"""【见run.py】FastAPI项目的静态文件配置"""

"""Path Operation Configuration 路径操作配置"""

@app04.post(
    "/path_operation_configuration",
    response_model=UserOut,
    # tags=["Path", "Operation", "Configuration"],
    summary="This is summary",
    description="This is description",
    response_description="This is response description",
    # deprecated=True,
    status_code=status.HTTP_200_OK
)
async def path_operation_configuration(user: UserIn):
    """Path Operation Configuration 路径操作配置"""
    return user.dict()
