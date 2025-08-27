# src/repository/users.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:

    res = await db.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()


async def create_user(body: UserModel, password_hash: str, db: AsyncSession) -> User:

    user = User(username=body.username, email=body.email, password=password_hash)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_token(user: User, token: Optional[str], db: AsyncSession) -> None:

    await db.execute(update(User).where(User.id == user.id).values(refresh_token=token))
    await db.commit()


async def set_role(user_id: int, role: str, db: AsyncSession) -> Optional[User]:

    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        return None
    user.role = role
    await db.commit()
    await db.refresh(user)
    return user


async def list_users(db: AsyncSession) -> list[User]:

    res = await db.execute(select(User).order_by(User.id))
    return list(res.scalars().all())
