# src/services/auth.py
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_EXPIRE_MIN,
    REFRESH_EXPIRE_DAYS,
)
from src.database.db import get_db
from src.repository import users as repo_users


class Auth:
    """
    Сервіс аутентифікації/авторизації:
    - хеш/перевірка пароля
    - видача access/refresh токенів
    - валідація refresh токена
    - Отримання поточного користувача з access токена (FastAPI dependency)
    """    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    # --- Паролі ---
    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    # --- Токени ---
    async def create_access_token(
        self, data: dict, minutes: Optional[int] = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=minutes or ACCESS_EXPIRE_MIN  # type: ignore
        )
        to_encode.update(
            {"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"}
        )
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore

    async def create_refresh_token(self, data: dict, days: Optional[int] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            days=days or REFRESH_EXPIRE_DAYS  # type: ignore
        )
        to_encode.update(
            {"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"}
        )
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore

    async def decode_refresh_token(self, refresh_token: str) -> str:

        # Повертає email (sub) з refresh токена або кидає 401.
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore
            if payload.get("scope") != "refresh_token":
                raise HTTPException(status_code=401, detail="Invalid scope for token")
            sub = payload.get("sub")
            if not sub:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            return sub
        except JWTError:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )

    # --- Dependency: current user з access токена ---
    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
    ):
        """
        Дістає користувача за access токеном.
        Потребує токені: scope=access_token і sub=email.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore
            if payload.get("scope") != "access_token": 
                raise credentials_exception
            email = payload.get("sub")
            if not email:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await repo_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user


auth_service = Auth()
