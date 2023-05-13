'''
Author: AlexXuan xuanxiaoguang@gmail.com
Date: 2023-05-13 14:59:16
LastEditors: AlexXuan xuanxiaoguang@gmail.com
LastEditTime: 2023-05-13 15:43:18
FilePath: /fastapi-exp/coronavirus/schemas.py
'''
from datetime import datetime
from datetime import date as date_
from pydantic import BaseModel


class CreateData(BaseModel):
    date: date_
    confirmed: int
    deaths: int
    recovered: int


class CreateCity(BaseModel):
    province: str
    country: str
    country_code: str
    country_population: int


class ReadData(CreateData):
    id: int
    city_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ReadCity(CreateCity):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


