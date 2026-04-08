from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.engine import Connection

from app.db.database import get_db
from app.services.auth_service import get_current_user
from app.services.jwt_service import create_token
from app.services.user_service import UserService

router       = APIRouter()
user_service = UserService()


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


@router.post("/api/auth/login")
def login(body: LoginRequest, db: Connection = Depends(get_db)):
    user = user_service.authenticate(db=db, username=body.username, password=body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(sub=user["username"], name=user["username"], username=user["username"])
    return {"access_token": token, "token_type": "bearer", **user}


@router.post("/api/auth/register")
def register(body: RegisterRequest, db: Connection = Depends(get_db)):
    user = user_service.create_user(db=db, username=body.username, password=body.password, email=body.email)
    if not user:
        raise HTTPException(status_code=409, detail="Username already taken")
    token = create_token(sub=user["username"], name=user["username"], username=user["username"])
    return {"access_token": token, "token_type": "bearer", **user}


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return JSONResponse(user)


@router.get("/logout")
def logout():
    return JSONResponse({"message": "Logged out"})
