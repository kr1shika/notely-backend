from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Note schemas
class NoteCreate(BaseModel):
    title: Optional[str] = "Untitled"
    content: Optional[str] = ""

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_archived: Optional[bool] = None

class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_archived: bool

    class Config:
        from_attributes = True