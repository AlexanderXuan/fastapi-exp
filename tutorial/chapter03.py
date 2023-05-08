'''
Author: AlexanderXuan xuanxiaoguang@gmail.com
Date: 2023-05-07 19:53:57
LastEditors: AlexanderXuan xuanxiaoguang@gmail.com
LastEditTime: 2023-05-07 20:52:47
FilePath: /fastspi-exp/tutorial/chapter03.py
'''
from enum import Enum
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Path, Query, Cookie, Header

app03 = APIRouter()

"""Path Parameters and Numeric Validations 路径参数和数字验证"""

@app03.get("/path/parameters")
def path_params01():
    return {"message": "This is a message"}

@app03.get("/path/{parameters}")    # 函数顺序就是路由顺序
def path_params01(parameters: str):
    return {"message": f"This is a {parameters}"}


class CityName(str, Enum):
    Beijing = "Beijing China"
    Shanghai = "Shanghai China"

@app03.get("/enum/{city}")  # 枚举类型参数
async def latest(city: CityName):
    if city == CityName.Shanghai:
        return {"city_name": city, "confirmed": 1492, "deaths": 7}
    if city == CityName.Beijing:
        return {"city_name": city, "confirmed": 593, "deaths": 9}
    return {"city_name": city, "latest": "unknown"}

@app03.get("/files/{file_path:path}")  # 通过path parameter传递文件路径
def filepath(file_path: str):
    return f"The file path is {file_path}"

@app03.get("/path_/{num}")
def path_params_validate(
    num: int = Path(..., title="Your number", description="不可描述", gt=1, le=10)):
    return num

"""Query Parameters and String Validations 查询参数和字符串验证"""
@app03.get("/query")
def page_limits(page: int = 1, limit: Optional[int] = None):
    if limit:
        return {"page": page, "limit": limit}
    return {"page": page}

@app03.get("/query/bool/conversion")
def type_conversion(param: bool = False):
    return param

@app03.get("/query/validations")
def query_params_validate(
    value: str = Query(..., min_length=8, max_length=16, regex="^a"),
    values: List[str] = Query(default=["v1", "v2"], alias="alias_name")
):  # 多个查询参数的列表，参数别名
    return value, values

"""Request Body and Fields 请求体和字段"""

class CityInfo(BaseModel):
    name: str = Field(..., example="Beijing")
    country: str
    country_code: str = None
    country_population: int = Field(default=800, title="人口数量", description="国家的人口数量", gt=800)

    class Config:
        schema_extra = {
            "example": {
                "name": "Shanghai",
                "country": "China",
                "country_code": "CN",
                "country_population": 1400000000,
            }
        }

@app03.post("/request_body/city")
def city_info(city: CityInfo):
    print(city.name, city.country)
    return city.dict()

"""Request Body + Path Parameters + Query Parameters 多参数混合"""
@app03.put("/request_body/city/{name}")
def mix_city_info(
    name: str,
    city01: CityInfo,
    city02: CityInfo,   # Body 可以定义多个
    confirmed: int = Query(ge=0, description="确诊数", default=0),
    deaths: int = Query(ge=0, description="死亡数", default=0),
):
    if name == "Shanghai":
        return {"Shanghai": {"confirmed": confirmed, "deaths": deaths}}
    return city01.dict(), city02.dict()

"""Request Body - Nested Models 嵌套模型"""
class Data(BaseModel):
    city: List[CityInfo] = None # 定义数据格式嵌套的请求体
    date: date
    confirmed: int = Field(ge=0, description="确诊数", default=0)
    deaths: int = Field(ge=0, description="死亡数", default=0)
    recovered: int = Field(ge=0, description="治愈数", default=0)

@app03.put("/request_body/nested")
def nested_models(data: Data):
    return data


"""Cookie and Header Parameters Cookie和Header参数"""

@app03.get("/cookie")   # 效果只能用Postman测试
def cookie(cookie_id: Optional[str] = Cookie(None)):    # 定义cookie参数需要用Cookie类
    return {"cookie_id": cookie_id}

@app03.get("/header")
def header(user_agent: Optional[str] = Header(None, convert_underscores=True), x_token: List[str] = Header(None)):
    return {"User-Agent": user_agent, "x_token": x_token}
