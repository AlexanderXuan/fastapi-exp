'''
Author: AlexanderXuan xuanxiaoguang@gmail.com
Date: 2023-05-07 19:54:07
LastEditors: AlexXuan xuanxiaoguang@gmail.com
LastEditTime: 2023-05-12 08:51:23
FilePath: /fastapi-exp/tutorial/chapter06.py
'''
from datetime import datetime, timedelta
from typing import Optional, List, Union
from fastapi import APIRouter, Depends, Header, HTTPException,status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from passlib.context import CryptContext
from jose import JWTError, jwt


app06 = APIRouter()

"""OAuth2密码模式和FastAPI的OAuth2PasswordBearer"""
"""
OAuth2PasswordBearer是接收url作为参数的一个类：客户端会向该url发送username和password，然后得到一个token
OAuth2PasswordBearer并不会创建相应的URL路径操作，只是指明了客户端用来请求token的URL地址
当请求到来时，FastAPI会检查请求的Authorization头信息，如果没有找到Authorization头信息，或者头信息的内容不是Bearer token，那么FastAPI会返回401状态码（UNAUTHORISED）
"""

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/chapter06/token")   # 请求Token的URL为http://127.0.0.1:8000/chapter06/token

@app06.get("oauth2_password_bearer")
async def oauth2_password_bearer(token: str = Depends(oauth2_scheme)):
    return {"token": token}

"""基于Password和Bearer token的OAuth2认证"""
fake_users_db = {
    "john snow": {
        "username": "john snow",
        "full_name": "John Snow",
        "email": "johnsnow@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

def fake_hash_password(password: str):
    return "fakehashed" + password

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str


@app06.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    return {"access_token": user.username, "token_type": "bearer"}


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def fake_decode_token(token: str):
    user = get_user(fake_users_db, token)
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}, # 告知客户端如何进行认证
        )
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user

@app06.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


"""OAuth2 with Password (and hashing), Bearer with JWT tokens 开发基于JSON Web Tokens的OAuth2认证"""
fake_users_db.update({
    "john snow": {
        "username": "john snow",
        "full_name": "John Snow",
        "email": "johnsnow@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
})

# 生成密钥
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256" # 算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 过期时间

class Token(BaseModel):
    """返回给用户的Token"""
    access_token: str
    token_type: str 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # 用于加密密码的类

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/chapter06/jwt/token")   # 请求Token的URL为http://

def verify_password(plain_password: str, hashed_password: str):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def jwt_get_user(db, username: str):
    """获取用户"""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    
def jwt_authenticate_user(db, username: str, password: str):
    """验证用户"""
    user = jwt_get_user(db=db, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def jwt_create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app06.post("/jwt/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """登录"""
    user = jwt_authenticate_user(db=fake_users_db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt_create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


async def jwt_get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前用户"""
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = jwt_get_user(db=fake_users_db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def jwt_get_current_active_user(current_user: User = Depends(jwt_get_current_user)):
    """获取当前活跃用户"""
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

@app06.get("/jwt/users/me")
async def read_users_me(current_user: User = Depends(jwt_get_current_active_user)):
    return current_user

