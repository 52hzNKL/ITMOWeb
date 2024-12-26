from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from sqlalchemy.orm import Session
from db import schemas, crud, database 
import jwt
import bcrypt

SECRET_KEY = "helloguys"
ALGORITHM = "HS256"

app = FastAPI()


database.Base.metadata.create_all(bind=database.engine)


app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
templates = Jinja2Templates(directory="/app/website/templates")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict):
    to_encode = data.copy() 
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def check_password(plain_text_password, hashed_password):
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    db_user = crud.get_user_by_fields(db, username=user.username, email=user.email, name=user.name)
    
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(status_code=400, detail="Username already registered")
        if db_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        if db_user.name == user.name:
            raise HTTPException(status_code=400, detail="Name already registered")

    crud.create_user(db, user=user)

    return JSONResponse(
        status_code=201,
        content={"message": "User registered successfully"}
    )



@app.post("/login", response_model=schemas.UserResponse)
async def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user is None:
        return JSONResponse(
            status_code=401,
            content={"message": "Invalid username or password"}
        )
    if not check_password(user.password, db_user.password):  
        return JSONResponse(
            status_code=401,
            content={"message": "Invalid username or password"}
        )
    user_data = {
        "id": db_user.id
    }

    access_token = create_access_token(user_data)

    return JSONResponse(
        status_code=200,
        content={
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "is_active": db_user.is_active,
            "access_token": access_token
        }
    )

