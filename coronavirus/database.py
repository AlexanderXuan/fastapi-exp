'''
Author: AlexXuan xuanxiaoguang@gmail.com
Date: 2023-05-13 14:58:26
LastEditors: AlexXuan xuanxiaoguang@gmail.com
LastEditTime: 2023-05-13 22:42:45
FilePath: /fastapi-exp/coronavirus/database.py
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URI = 'sqlite:///./coronavirus.sqlite3'
# SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@host:port/database_name'    # MySQL或PostgreSQL的连接方法

engine = create_engine(
    # echo=True表示引擎将用repr()函数记录所有语句及其参数列表到日志
    # 由于SQLAlchemy是多线程，指定check_same_thread=False来让建立的对象任意线程都可使用，这个参数只有在用SQLite数据库时设置
    SQLALCHEMY_DATABASE_URI, echo=True, connect_args={'check_same_thread': False}
)

# 在SQLAlchemy中，CRUD都是通过会话(session)进行的，所以我们必须要先创建会话，每一个SessionLocal实例就是一个数据库session
# flush()是指发送数据库语句到数据库，但数据库不一定执行写入磁盘；commit()是指提交事务，将变更保存到数据库文件
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=True)

# 创建基本的映射类
Base = declarative_base()

