from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
# from sqlalchemy.orm import relationship
from database import Base
# from datetime import datetime


# Таблица пользователей
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True)
    email = Column(String, default="")
    password = Column(String)
    date_of_registration = Column(DateTime)

    # posts = relationship('Posts', backref='user', cascade='all,delete')


class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    text = Column(String)
    date_added = Column(DateTime)
    id_user = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # user = relationship('Users', backref='posts')
