from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel
from src.repository import users as repository_users
from src.services.auth import auth_service


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


# Реєстрація нового користувача
@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(body: UserModel, db: AsyncSession = Depends(get_db)):
    exist = await repository_users.get_user_by_email(body.email, db)
    if exist:
        raise HTTPException(status_code=409, detail="Account already exists")
    hashed = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, hashed, db)
    return {"user": new_user, "detail": "User successfully created"}


# Логін користувача
@router.post("/login", response_model=TokenModel)
async def login(
    form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await repository_users.get_user_by_email(form.username, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email")
    if not auth_service.verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    access = await auth_service.create_access_token(data={"sub": user.email})
    refresh = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh, db)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


# Оновлення токенів
@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    stored_refresh: str | None = getattr(user, "refresh_token", None)
    if stored_refresh != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access = await auth_service.create_access_token(data={"sub": email})
    refresh = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh, db)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}
