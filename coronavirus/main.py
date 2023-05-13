'''
Author: AlexXuan xuanxiaoguang@gmail.com
Date: 2023-05-13 14:59:50
LastEditors: AlexXuan xuanxiaoguang@gmail.com
LastEditTime: 2023-05-13 23:46:19
FilePath: /fastapi-exp/coronavirus/main.py
'''
import requests
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks

from sqlalchemy.orm import Session

from pydantic import HttpUrl

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from coronavirus import schemas, crud
from coronavirus.database import SessionLocal, engine, Base
from coronavirus.models import City, Data

application = APIRouter()

templates = Jinja2Templates(directory='./coronavirus/templates')

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@application.post('/create_city', response_model=schemas.ReadCity)
def create_city(city: schemas.CreateCity, db: Session = Depends(get_db)):
    db_city = crud.get_city_by_name(db, name=city.province)
    if db_city:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='City already registered')
    return crud.create_city(db=db, city=city)

@application.get("/get_city/{city}", response_model=schemas.ReadCity)
def get_city(city: str, db: Session = Depends(get_db)):
    db_city = crud.get_city_by_name(db, name=city)
    if db_city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
    return db_city

@application.get('/get_cities', response_model=List[schemas.ReadCity])
def get_cities(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    cities = crud.get_cities(db, skip=skip, limit=limit)
    return cities

@application.post('/create_data', response_model=schemas.ReadData)
def create_data_for_city(city: str, data: schemas.CreateData, db: Session = Depends(get_db)):
    db_city = crud.get_city_by_name(db, name=city)
    data = crud.create_city_data(db=db, data=data, city_id=db_city.id)
    return data

@application.get('/get_data', response_model=List[schemas.ReadData])
def get_data(city: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    data = crud.get_data(db, city=city, skip=skip, limit=limit)
    return data


def bg_task(url: HttpUrl, db: Session):
    """这里注意一个坑，不要在后台任务的参数中db: Session = Depends(get_db)这样导入依赖"""
    city_data = requests.get(f"{url}?source=jhu&country_code=CN&timelines=false")

    if 200 == city_data.status_code:
        db.query(City).delete() # 同步数据前先清空数据
        for location in city_data.json()['locations']:
            city = {
                "province": location['province'],
                "country": location['country'],
                "country_code": location['country_code'],
                "country_population": location['country_population']
            }
            crud.create_city(db=db, city=schemas.CreateCity(**city))
    
    coronavirus_data = requests.get(f"{url}?source=jhu&country_code=CN&timelines=true")
    if 200 == coronavirus_data.status_code:
        db.query(Data).delete()
        for city in coronavirus_data.json()['locations']:
            db_city = crud.get_city_by_name(db, name=city['province'])
            for date, confirmed in city['timelines']['confirmed']['timeline'].items():
                data = {
                    "date": date.split('T')[0],
                    "confirmed": confirmed,
                    "deaths": city['timelines']['deaths']['timeline'][date],
                    "recovered": city['timelines']['recovered']['timeline'][date],
                }
                crud.create_city_data(db=db, data=schemas.CreateData(**data), city_id=db_city.id)
    pass

@application.get("/sync_coronavirus_data/jhu")
def sync_coronavirus_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """从Johns Hopkins University同步COVID-19数据"""
    background_tasks.add_task(bg_task, "https://coronavirus-tracker-api.herokuapp.com/v2/locations", db)
    return {"message": "正在后台同步数据..."}

@application.get('/')
def coronavirus(request: Request, city: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    data = crud.get_data(db, city=city, skip=skip, limit=limit)
    return templates.TemplateResponse('home.html', {'request': request, 
                                                    'data': data, 
                                                    "sync_data_url": "/coronavirus/sync_coronavirus_data/jhu"
                                                    })

# a demo for directly return html file, not use jinja2 templates
# @application.get('/')
# def index():
#     html_file = open('./coronavirus/templates/home.html', 'r', encoding='utf-8').read()
#     return html_file
