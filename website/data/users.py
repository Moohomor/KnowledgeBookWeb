import datetime

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime

from .db_session import SqlAlchemyBase


class User(UserMixin, SqlAlchemyBase):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, index=True, unique=True)
    token = Column(Integer, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    joined = Column(DateTime, default=datetime.datetime.now)
