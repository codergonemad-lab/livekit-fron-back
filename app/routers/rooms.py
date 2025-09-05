from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import User, Room, RoomParticipant
from ..schemas import (
    RoomCreate,
    Room as RoomSchema,
    RoomWithParticipants,
    LiveKitTokenRequest,
    LiveKitTokenResponse
)
from ..auth import get_current_active_user
from ..livekit_service import livekit_service
import uuid

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("/", response_model=RoomSchema)
async def create_room(
    room: RoomCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new room."""
    # Generate unique room ID
    room_id = f"room_{uuid.uuid4().hex[:8]}"
    
    try:
        # Create room in LiveKit
        livekit_room = await livekit_service.create_room(room_id)
        
        # Create room in database
        db_room = Room(
            name=room.name,
            room_id=room_id,
            description=room.description,
            creator_id=current_user.id,
            max_participants=room.max_participants
        )
        
        db.add(db_room)
        db.commit()
        db.refresh(db_room)
        
        return db_room
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create room: {str(e)}"
        )


@router.get("/", response_model=List[RoomWithParticipants])
def list_rooms(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all active rooms with participant counts."""
    rooms = db.query(
        Room,
        func.count(RoomParticipant.id).label("participants_count")
    ).outerjoin(
        RoomParticipant,
        (Room.id == RoomParticipant.room_id) & (RoomParticipant.is_connected == True)
    ).filter(
        Room.is_active == True
    ).group_by(Room.id).offset(skip).limit(limit).all()
    
    result = []
    for room, participants_count in rooms:
        creator = db.query(User).filter(User.id == room.creator_id).first()
        room_data = RoomWithParticipants(
            **room.__dict__,
            participants_count=participants_count,
            creator=creator
        )
        result.append(room_data)
    
    return result


@router.get("/{room_id}", response_model=RoomWithParticipants)
def get_room(
    room_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific room by ID."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    participants_count = db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.is_connected == True
    ).count()
    
    creator = db.query(User).filter(User.id == room.creator_id).first()
    
    return RoomWithParticipants(
        **room.__dict__,
        participants_count=participants_count,
        creator=creator
    )


@router.post("/{room_id}/join", response_model=LiveKitTokenResponse)
async def join_room(
    room_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Join a room and get LiveKit access token."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if not room.is_active:
        raise HTTPException(status_code=400, detail="Room is not active")
    
    # Check if user is already in the room
    existing_participant = db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.user_id == current_user.id,
        RoomParticipant.is_connected == True
    ).first()
    
    if not existing_participant:
        # Add user as participant
        participant = RoomParticipant(
            room_id=room_id,
            user_id=current_user.id,
            is_connected=True
        )
        db.add(participant)
        db.commit()
    
    # Generate LiveKit token
    try:
        token = livekit_service.generate_access_token(
            room_name=room.room_id,
            participant_name=current_user.username
        )
        
        return LiveKitTokenResponse(
            token=token,
            room_url=f"{livekit_service.livekit_url}?token={token}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate access token: {str(e)}"
        )


@router.post("/{room_id}/leave")
def leave_room(
    room_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Leave a room."""
    participant = db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.user_id == current_user.id,
        RoomParticipant.is_connected == True
    ).first()
    
    if not participant:
        raise HTTPException(status_code=400, detail="You are not in this room")
    
    participant.is_connected = False
    participant.left_at = func.now()
    db.commit()
    
    return {"message": "Successfully left the room"}


@router.delete("/{room_id}")
async def delete_room(
    room_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a room (only creator can delete)."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.creator_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the room creator can delete the room"
        )
    
    try:
        # Delete room from LiveKit
        await livekit_service.delete_room(room.room_id)
        
        # Mark room as inactive in database
        room.is_active = False
        db.commit()
        
        return {"message": "Room deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete room: {str(e)}"
        )


@router.get("/{room_id}/participants")
async def get_room_participants(
    room_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get participants in a room from LiveKit."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    try:
        participants = await livekit_service.get_room_participants(room.room_id)
        return {"participants": participants}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get participants: {str(e)}"
        )
