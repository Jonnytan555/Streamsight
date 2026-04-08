import os
from jose import JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.services.jwt_service import verify_token

_DEV_USER = {"sub": "dev-user", "name": "Dev User", "email": "dev@local"}
_IS_DEV   = os.getenv("SERVER", "DEV") != "PRD"

# Tells FastAPI where the login endpoint is — enables the lock icon in Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=not _IS_DEV)


def get_current_user(token: str | None = Depends(oauth2_scheme)) -> dict:
    if _IS_DEV:
        return _DEV_USER
    if not token:
        raise HTTPException(status_code=401, detail="Not logged in")
    try:
        return verify_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_user_id(user: dict = Depends(get_current_user)) -> str:
    return str(user.get("sub"))
