from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.db import get_db
from src.database.models import User
from src.schemas import UserDb
from src.repository.users import list_users, set_role
from src.services.permissions import access_admin_only, Role

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserDb], dependencies=[Depends(access_admin_only)])
async def get_users(db: AsyncSession = Depends(get_db)):
    return await list_users(db)


@router.put(
    "/{user_id}/role/{role}",
    response_model=UserDb,
    dependencies=[Depends(access_admin_only)],
)
async def change_role(user_id: int, role: Role, db: AsyncSession = Depends(get_db)):
    user = await set_role(user_id, role.value, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
