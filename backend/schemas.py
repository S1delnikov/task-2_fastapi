from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class UserRegSchema(BaseModel):
    username: str
    email: str | None = None
    password: str
    date_of_registration: datetime = datetime.now()


class UserInSchema(BaseModel):
    username: str
    password: str


class UserOutSchema(BaseModel):
    id: int
    username: str


class PostSchema(BaseModel):
    title: str
    text: str
    date_added: datetime = datetime.now()
    # id_user: int