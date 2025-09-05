from livekit import api
from .config import settings


class LiveKitService:
    def __init__(self):
        self.api_key = settings.livekit_api_key
        self.api_secret = settings.livekit_api_secret
        self.livekit_url = settings.livekit_url
        
        # Get the base HTTP URL for API calls
        self.http_url = self.livekit_url.replace('wss://', 'https://').replace('ws://', 'http://')

    def generate_access_token(self, room_name: str, participant_name: str) -> str:
        """Generate a LiveKit access token for a participant to join a room."""
        token = api.AccessToken(self.api_key, self.api_secret)
        token.with_identity(participant_name)
        token.with_name(participant_name)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        ))
        
        return token.to_jwt()

    async def create_room(self, room_name: str) -> dict:
        """Create a room in LiveKit."""
        # For now, we'll create a mock response since room creation happens automatically
        # when the first participant joins. We'll return a simple success response.
        return {
            "name": room_name,
            "sid": f"RM_{room_name}",
            "creation_time": 0,
            "num_participants": 0
        }

    async def delete_room(self, room_name: str) -> bool:
        """Delete a room from LiveKit."""
        try:
            room_service = api.room_service.RoomService(
                self.http_url,
                self.api_key,
                self.api_secret
            )
            await room_service.delete_room(
                api.DeleteRoomRequest(room=room_name)
            )
            return True
        except Exception as e:
            # Room might not exist, which is fine for our use case
            print(f"Room deletion note: {str(e)}")
            return True

    async def list_rooms(self) -> list:
        """List all active rooms in LiveKit."""
        try:
            room_service = api.room_service.RoomService(
                self.http_url,
                self.api_key,
                self.api_secret
            )
            rooms = await room_service.list_rooms(api.ListRoomsRequest())
            return [
                {
                    "name": room.name,
                    "sid": room.sid,
                    "num_participants": room.num_participants,
                    "creation_time": room.creation_time
                }
                for room in rooms.rooms
            ]
        except Exception as e:
            print(f"List rooms note: {str(e)}")
            return []

    async def get_room_participants(self, room_name: str) -> list:
        """Get participants in a specific room."""
        try:
            room_service = api.room_service.RoomService(
                self.http_url,
                self.api_key,
                self.api_secret
            )
            participants = await room_service.list_participants(
                api.ListParticipantsRequest(room=room_name)
            )
            return [
                {
                    "identity": p.identity,
                    "name": p.name,
                    "sid": p.sid,
                    "joined_at": p.joined_at,
                    "state": p.state.name if p.state else "UNKNOWN"
                }
                for p in participants.participants
            ]
        except Exception as e:
            print(f"Get participants note: {str(e)}")
            return []


# Singleton instance
livekit_service = LiveKitService()
