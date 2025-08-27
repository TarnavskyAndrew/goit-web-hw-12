from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime


# -------- USER ----------
class UserModel(BaseModel):
    username: Optional[str] = Field(default=None, min_length=2, max_length=32)
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)


class UserDb(BaseModel):
    id: int
    username: Optional[str]
    email: EmailStr
    created_at: datetime
    avatar: Optional[str] = None
    role: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# -------- CONTACT ----------
class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    extra: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int

    class Config:
        from_attributes = True
