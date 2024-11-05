from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    username: str
    email: str
    access_token: str
    token_type: str
    is_active: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class MessageBase(BaseModel):
    content: str
    sender_name : str

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    content: str
    chat_id: int
    timestamp: datetime
    sender_id: int

    class Config:
        from_attributes = True

class ChatMessagesResponse(BaseModel):
    messages: List[MessageResponse]
    chat_id: int
    chat_title: str
    
class ChatBase(BaseModel):
    title: str
    owner_id: int
    guess_id: int

class ChatCreate(ChatBase):
    pass

class ChatResponse(ChatBase):
    id: int
    owner_id: int
    messages: List[MessageResponse] = []

    class Config:
        orm_mode = True
