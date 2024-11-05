from fastapi import FastAPI, Depends, Request, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from db import crud
from db import schemas
from db.database import SessionLocal
import os
from fastapi.responses import JSONResponse
from typing import List
from typing import Any
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWTError

app = FastAPI()
# Static files
app.mount("/chat-static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "chat-static")), name="chat-static")
templates = Jinja2Templates(directory="/app/chat/templates")

SECRET_KEY = "helloguys"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        username: str = payload.get("username")

        if user_id is None or username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return {"id": user_id, "username": username}
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/chat", response_class=HTMLResponse)
async def load_chat_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("box.html", {"request": request})
    
@app.get("/search-user")
async def search_user(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=username)
    if user:
        return JSONResponse(
        status_code=200,
        content={
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email
        }
    )
@app.get("/messages/{guess_id}", response_model=schemas.ChatMessagesResponse)
def get_chat_messages(guess_id: int, token:str, db: Session = Depends(get_db)):
    user_info = verify_access_token(token)
    user = crud.get_user_by_id(db, user_info.get('id'))
    guess = crud.get_user_by_id(db, guess_id)
    chatPayload = {"title": f"{guess.name} and {user.name}", "guess_id":guess_id, "owner_id":user.id}
    chatPayload = schemas.ChatCreate(**chatPayload)
    chat = crud.get_chat(db, guess_id, user.id)
    if not chat:
        chat = crud.create_chat(db, chatPayload)
    messages = crud.get_messages(db, chat.id)

    return {"messages": messages, "chat_id": chat.id, "chat_title": chat.title}

@app.get("/get_user")
async def get_user_infor(token:str, db: Session = Depends(get_db)):
    user_info = verify_access_token(token)
    return JSONResponse(
        status_code=200,
        content={
            "id": user_info.get('id')
        })

@app.get("/chats/recent_messages")
async def get_recent_messages(token: str, db: Session = Depends(get_db)):
    user_info = verify_access_token(token)
    owner = crud.get_user_by_id(db, user_info.get('id'))
    chats, guess = crud.get_user_chats_with_latest_message(db, owner_id=owner.id)
    return {
        "chats": chats,
        "guess": guess
    }

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            content = data.get("content")
            sender_id = data.get("sender_id")

            if not content or not sender_id:
                continue

            user = crud.get_user_by_id(db, sender_id)
            sender_name = user.name

            message_create = schemas.MessageCreate(content=content, sender_name=sender_name)
            try:
                new_message = crud.create_message(db=db, message=message_create, user_id=sender_id, chat_id=chat_id)
            except Exception as e:
                await websocket.send_text(f"Error saving message: {str(e)}")
                continue

            await manager.broadcast(f"{sender_name}: {new_message.content}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"WebSocket disconnected from chat {chat_id}")

