from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserInDB(User):
    hashed_password: str


# Room Schemas
class RoomBase(BaseModel):
    name: str
    description: Optional[str] = None
    max_participants: Optional[int] = 50


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    max_participants: Optional[int] = None


class Room(RoomBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    room_id: str
    creator_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class RoomWithParticipants(Room):
    participants_count: int
    creator: User


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# LiveKit Schemas
class LiveKitTokenRequest(BaseModel):
    room_name: str
    participant_name: str


class LiveKitTokenResponse(BaseModel):
    token: str
    room_url: str
