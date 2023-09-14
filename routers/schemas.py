from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    user_type: str = None
    password: str


class UserDisplay(BaseModel):
    username: str
    email: EmailStr
    user_type:str

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    image_url: str
    image_url_type: str
    caption: str


# for post display
class User(BaseModel):
    username: str

    class Config:
        orm_mode = True

class Comment(BaseModel):
    id:int
    comment: str
    username: str
    timestamp: datetime

    class Config:
        orm_mode = True


class PostDisplay(BaseModel):
    id: int
    image_url: str
    image_url_type: str
    caption: str
    timestamp: datetime
    user: User

    comments: list[Comment]

    class Config:
        orm_mode = True

class UserAuth(BaseModel):
    id: int
    username: str
    email: EmailStr

class CommentBase(BaseModel):
    comment: str

    class Config:
        orm_mode = True


class CommentDisplay(BaseModel):
    id:int
    comment: str
    username: str
    timestamp: datetime

    class Config:
        orm_mode = True
