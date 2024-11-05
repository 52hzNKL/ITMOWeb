from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    owner_chats = relationship("Chat", foreign_keys="[Chat.owner_id]", back_populates="owner")
    guess_chats = relationship("Chat", foreign_keys="[Chat.guess_id]", back_populates="guess")
    messages = relationship("Message", back_populates="sender")

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)  
    owner_id = Column(Integer, ForeignKey("users.id"))
    guess_id = Column(Integer, ForeignKey("users.id")) 

    messages = relationship("Message", back_populates="chat")

    owner = relationship("User", foreign_keys=[owner_id], back_populates="owner_chats")
    guess = relationship("User", foreign_keys=[guess_id], back_populates="guess_chats")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    sender_name = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    sender_id = Column(Integer, ForeignKey("users.id"))
    chat_id = Column(Integer, ForeignKey("chats.id"))

    sender = relationship("User", back_populates="messages")
    chat = relationship("Chat", back_populates="messages")
