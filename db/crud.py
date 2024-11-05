from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import func, or_
from .models import Chat, Message, User
import bcrypt

def hash_password(plain_text_password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed_password

def create_user(db: Session, user: schemas.UserCreate):
    password = hash_password(user.password).decode('utf-8') 
    db_user = models.User(username=user.username, email=user.email, password=password, name=user.name)  
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_chat(db: Session, chat: schemas.ChatCreate):
    db_chat = models.Chat(
        title=chat.title,
        owner_id=chat.owner_id,
        guess_id=chat.guess_id
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def create_message(db: Session, message: schemas.MessageCreate, user_id: int, chat_id: int):
    db_message = models.Message(**message.dict(), sender_id=user_id, chat_id=chat_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message



def get_user_by_fields(db: Session, username: str, email: str, name: str):
    return db.query(models.User).filter(
        or_(
            models.User.username == username,
            models.User.email == email,
            models.User.name == name
        )
    ).first()

def get_user_by_id(db: Session, id: int):
    return db.query(models.User).filter(models.User.id == id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_chat(db: Session, guess_id:int, owner_id:int):
    return db.query(models.Chat).filter(
        ((models.Chat.owner_id == owner_id) & (models.Chat.guess_id == guess_id)) |
        ((models.Chat.owner_id == guess_id) & (models.Chat.guess_id == owner_id))
    ).first()

def get_messages(db: Session, chat_id: int):
    return db.query(models.Message).filter(models.Message.chat_id == chat_id).all()

def get_user_chats_with_latest_message(db: Session, owner_id: int):
    subquery = (
        db.query(
            Message.chat_id,
            func.max(Message.timestamp).label("latest_message_time")
        )
        .group_by(Message.chat_id)
        .subquery()
    )

    results = (
        db.query(
            Chat.id.label("chat_id"),
            Chat.title.label("chat_name"),
            Chat.guess_id.label("guess_id"),
            Chat.owner_id.label("owner_id"),
            Message.content.label("last_message_content"),
            Message.sender_name.label("last_message_sender"),
            Message.timestamp.label("last_message_time")
        )
        .join(Message, Message.chat_id == Chat.id)
        .join(subquery, (Message.chat_id == subquery.c.chat_id) & (Message.timestamp == subquery.c.latest_message_time))
        .filter(or_(Chat.owner_id == owner_id, Chat.guess_id == owner_id))
        .all()
    )

    chat_list = []
    for chat in results:
        chat_list.append({
            "id": chat.chat_id,
            "name": chat.chat_name,
            "guess_id": chat.guess_id,
            "owner_id": chat.owner_id,
            "last_message": {
                "content": chat.last_message_content,
                "sender_name": chat.last_message_sender,
                "timestamp": chat.last_message_time
            }
        })
    guess = []
    for chat in chat_list:
        takeguess = get_user_by_id(db, chat['guess_id'])
        if takeguess.id == owner_id:
            takeguess = get_user_by_id(db, chat['owner_id'])
            guess.append(takeguess)
        else:
            guess.append(takeguess)
    return chat_list, guess
