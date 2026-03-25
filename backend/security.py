import os, secrets
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import database

SECRET_KEY  = os.getenv("JWT_SECRET", "super-secret-change-in-production")
ALGORITHM   = "HS256"
EXPIRE_DAYS = int(os.getenv("JWT_EXPIRE_DAYS", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer      = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(user_id: int) -> str:
    exp = datetime.utcnow() + timedelta(days=EXPIRE_DAYS)
    return jwt.encode({"sub": str(user_id), "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)

def generate_api_token() -> str:
    return secrets.token_urlsafe(32)


async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    token = creds.credentials
    exc   = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # 1. JWT (browser session)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = await database.fetch_one(
            "SELECT id, username, email FROM users WHERE id = :id",
            {"id": int(payload["sub"])}
        )
        if user:
            return dict(user)
    except JWTError:
        pass

    # 2. Static Bearer Token (Apple Shortcuts)
    user = await database.fetch_one(
        "SELECT id, username, email FROM users WHERE api_token = :t", {"t": token}
    )
    if user:
        return dict(user)

    raise exc
