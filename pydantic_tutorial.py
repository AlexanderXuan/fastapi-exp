'''
Author: AlexanderXuan xuanxiaoguang@gmail.com
Date: 2023-05-07 16:56:42
LastEditors: AlexanderXuan xuanxiaoguang@gmail.com
LastEditTime: 2023-05-07 17:45:26
FilePath: /fastspi-exp/pydantic_tutorial.py
'''
from datetime import datetime, date
from pydantic import BaseModel, ValidationError, constr
from typing import List, Optional
from pathlib import Path

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.declarative import declarative_base


class User(BaseModel):
    id: int
    name: str = "John Doe"
    signup_ts: Optional[datetime] = None
    friends: List[int] = [] # int 或者可转为int的类型

external_data = {
    "id": "123",
    "signup_ts": "2017-06-01 12:22",
    "friends": [1, "2", b"3"],
}

user = User(**external_data)
print(user.id, user.friends)
print(repr(user.signup_ts))
print(user.dict())


# 校验失败处理
try:
    User(id=1, signup_ts=datetime.today(), friends=[1, 2, "not number"])
except ValidationError as e:
    print(e.json())
print(user.dict())
print(user.json())
print(user.copy())
print(User.parse_obj(obj=external_data))
print(User.parse_raw('{"id": "123", "signup_ts": "2017-06-01 12:22", "friends": [1, "2", "3"]}'))

path = Path('user.json')
path.write_text('{"id": "123", "signup_ts": "2017-06-01 12:22", "friends": [1, "2", "3"]}')
print(User.parse_file('user.json'))

print(user.schema())
print(user.schema_json())


print(User.__fields__.keys())   # 定义模型类的时候，所有字段都注明类型，字段顺序就不会乱


# 递归模型
class Sound(BaseModel):
    sound: str

class Dog(BaseModel):
    birthday: date
    weight: float = Optional[None]
    sound: List[Sound] # 嵌套另一个类

dog = Dog(birthday=date.today(), weight=6.66, sound=[{"sound": "wang wang ~"}, {"sound": "ying ying ~"}])

print(dog.dict())

# ORM模型：SQLAlchemy 从类实例创建符合ORM对象的模型

Base = declarative_base()
class CompanyOrm(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, nullable=False)
    public_key = Column(String(20), index=True, nullable=False, unique=True)
    name = Column(String(63), unique=True)
    domains = Column(ARRAY(String(255)))

class CompanyModel(BaseModel):
    id: int
    public_key: constr(max_length=20)
    name: constr(max_length=63)
    domains: List[constr(max_length=255)]

    class Config:
        orm_mode = True
    
co_orm = CompanyOrm(
    id = 123,
    public_key = 'foobar',
    name = 'Testing',
    domains = ['example.com', 'foobar.com']
)

print(CompanyModel.from_orm(co_orm))
# pydantic 支持类型 https://docs.pydantic.dev/latest/usage/types/