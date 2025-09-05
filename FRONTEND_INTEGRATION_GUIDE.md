# LiveKit Video Calling Backend - Frontend Integration Guide

This document provides complete instructions for frontend developers on how to integrate with the LiveKit video calling backend.

## 📋 Table of Contents

1. [Backend Overview](#backend-overview)
2. [Authentication Flow](#authentication-flow)
3. [Room Management](#room-management)
4. [Video Calling Integration](#video-calling-integration)
5. [Frontend Implementation Steps](#frontend-implementation-steps)
6. [API Reference](#api-reference)
7. [Code Examples](#code-examples)
8. [Error Handling](#error-handling)
9. [Testing](#testing)
10. [Deployment Considerations](#deployment-considerations)

## 🎯 Backend Overview

### Base URL
```
Development: http://localhost:8000
Production: [Your production URL]
```

### Tech Stack
- **Backend**: FastAPI + PostgreSQL
- **Video**: LiveKit Cloud
- **Authentication**: JWT tokens
- **Database**: User and room management

### Key Features
- ✅ User registration and authentication
- ✅ Room creation and management  
- ✅ LiveKit token generation
- ✅ Participant tracking
- ✅ Real-time video calling

---

## 🔐 Authentication Flow

### 1. User Registration
```http
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-09-05T10:30:00Z"
}
```

### 2. User Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=secure_password
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Get Current User
```http
GET /auth/me
Authorization: Bearer {jwt_token}
```

---

## 🏠 Room Management

### 1. Create a Room
```http
POST /rooms/
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "name": "Team Meeting",
  "description": "Weekly team sync",
  "max_participants": 10
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Team Meeting",
  "room_id": "room_abcd1234",
  "description": "Weekly team sync",
  "creator_id": 1,
  "max_participants": 10,
  "is_active": true,
  "created_at": "2025-09-05T10:30:00Z"
}
```

### 2. List All Rooms
```http
GET /rooms/
Authorization: Bearer {jwt_token}
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Team Meeting",
    "room_id": "room_abcd1234",
    "description": "Weekly team sync",
    "creator_id": 1,
    "max_participants": 10,
    "is_active": true,
    "created_at": "2025-09-05T10:30:00Z",
    "participants_count": 3,
    "creator": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "full_name": "John Doe"
    }
  }
]
```

### 3. Join a Room (Get LiveKit Token)
```http
POST /rooms/{room_id}/join
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "room_url": "wss://your-livekit-server.livekit.cloud?token=..."
}
```

### 4. Leave a Room
```http
POST /rooms/{room_id}/leave
Authorization: Bearer {jwt_token}
```

### 5. Get Room Participants
```http
GET /rooms/{room_id}/participants
Authorization: Bearer {jwt_token}
```

---

## 🎥 Video Calling Integration

### LiveKit Configuration
```javascript
const LIVEKIT_URL = 'wss://osadho-m62vhfz7.livekit.cloud';
// Token comes from /rooms/{id}/join endpoint
```

### Required Libraries

#### For Web (React/Vue/Vanilla JS)
```bash
npm install livekit-client
```

#### For React Native
```bash
npm install @livekit/react-native
```

#### For Flutter
```yaml
dependencies:
  livekit_client: ^latest
```

---

## 🛠️ Frontend Implementation Steps

### Step 1: Setup Authentication State Management

```javascript
// auth.js
class AuthManager {
  constructor() {
    this.token = localStorage.getItem('jwt_token');
    this.user = null;
  }

  async login(username, password) {
    const response = await fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${username}&password=${password}`
    });
    
    const data = await response.json();
    if (response.ok) {
      this.token = data.access_token;
      localStorage.setItem('jwt_token', this.token);
      await this.getCurrentUser();
      return true;
    }
    throw new Error(data.detail);
  }

  async getCurrentUser() {
    const response = await fetch('http://localhost:8000/auth/me', {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    
    if (response.ok) {
      this.user = await response.json();
      return this.user;
    }
    return null;
  }

  logout() {
    this.token = null;
    this.user = null;
    localStorage.removeItem('jwt_token');
  }

  isAuthenticated() {
    return !!this.token;
  }

  getAuthHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }
}
```

### Step 2: Room Management Service

```javascript
// roomService.js
class RoomService {
  constructor(authManager) {
    this.auth = authManager;
    this.baseUrl = 'http://localhost:8000';
  }

  async createRoom(roomData) {
    const response = await fetch(`${this.baseUrl}/rooms/`, {
      method: 'POST',
      headers: this.auth.getAuthHeaders(),
      body: JSON.stringify(roomData)
    });
    
    if (!response.ok) {
      throw new Error(await response.text());
    }
    
    return response.json();
  }

  async listRooms() {
    const response = await fetch(`${this.baseUrl}/rooms/`, {
      headers: this.auth.getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(await response.text());
    }
    
    return response.json();
  }

  async joinRoom(roomId) {
    const response = await fetch(`${this.baseUrl}/rooms/${roomId}/join`, {
      method: 'POST',
      headers: this.auth.getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(await response.text());
    }
    
    return response.json();
  }

  async leaveRoom(roomId) {
    const response = await fetch(`${this.baseUrl}/rooms/${roomId}/leave`, {
      method: 'POST',
      headers: this.auth.getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(await response.text());
    }
    
    return response.json();
  }

  async getRoomParticipants(roomId) {
    const response = await fetch(`${this.baseUrl}/rooms/${roomId}/participants`, {
      headers: this.auth.getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(await response.text());
    }
    
    return response.json();
  }
}
```

### Step 3: Video Call Component

```javascript
// videoCall.js
import { Room, connect, createLocalTracks } from 'livekit-client';

class VideoCallManager {
  constructor(roomService) {
    this.roomService = roomService;
    this.room = null;
    this.localTracks = [];
    this.isConnected = false;
  }

  async joinVideoCall(roomId) {
    try {
      // Get LiveKit token from backend
      const { token, room_url } = await this.roomService.joinRoom(roomId);
      
      // Extract LiveKit URL (remove token parameter)
      const livekitUrl = room_url.split('?')[0];
      
      // Create room instance
      this.room = new Room({
        adaptiveStream: true,
        dynacast: true,
      });

      // Setup event listeners
      this.setupEventListeners();

      // Connect to LiveKit
      await this.room.connect(livekitUrl, token);
      
      // Enable camera and microphone
      await this.enableMedia();
      
      this.isConnected = true;
      return this.room;
      
    } catch (error) {
      console.error('Failed to join video call:', error);
      throw error;
    }
  }

  setupEventListeners() {
    this.room.on('trackSubscribed', (track, publication, participant) => {
      console.log('Track subscribed:', track.kind, participant.identity);
      
      if (track.kind === 'video' || track.kind === 'audio') {
        const element = track.attach();
        this.onTrackSubscribed?.(element, track, participant);
      }
    });

    this.room.on('trackUnsubscribed', (track, publication, participant) => {
      track.detach();
      this.onTrackUnsubscribed?.(track, participant);
    });

    this.room.on('localTrackPublished', (publication, participant) => {
      const track = publication.track;
      if (track) {
        const element = track.attach();
        this.onLocalTrackPublished?.(element, track, participant);
      }
    });

    this.room.on('participantConnected', (participant) => {
      console.log('Participant connected:', participant.identity);
      this.onParticipantConnected?.(participant);
    });

    this.room.on('participantDisconnected', (participant) => {
      console.log('Participant disconnected:', participant.identity);
      this.onParticipantDisconnected?.(participant);
    });

    this.room.on('disconnected', () => {
      console.log('Disconnected from room');
      this.isConnected = false;
      this.onDisconnected?.();
    });
  }

  async enableMedia() {
    try {
      this.localTracks = await createLocalTracks({
        audio: true,
        video: true,
      });

      for (const track of this.localTracks) {
        await this.room.localParticipant.publishTrack(track);
      }
    } catch (error) {
      console.error('Failed to enable media:', error);
      throw error;
    }
  }

  async toggleCamera() {
    const videoTrack = this.localTracks.find(track => track.kind === 'video');
    if (videoTrack) {
      if (videoTrack.isMuted) {
        await videoTrack.unmute();
      } else {
        await videoTrack.mute();
      }
      return !videoTrack.isMuted;
    }
    return false;
  }

  async toggleMicrophone() {
    const audioTrack = this.localTracks.find(track => track.kind === 'audio');
    if (audioTrack) {
      if (audioTrack.isMuted) {
        await audioTrack.unmute();
      } else {
        await audioTrack.mute();
      }
      return !audioTrack.isMuted;
    }
    return false;
  }

  async disconnect() {
    if (this.room) {
      await this.room.disconnect();
      this.room = null;
      this.localTracks = [];
      this.isConnected = false;
    }
  }

  // Event handler setters
  setEventHandlers(handlers) {
    this.onTrackSubscribed = handlers.onTrackSubscribed;
    this.onTrackUnsubscribed = handlers.onTrackUnsubscribed;
    this.onLocalTrackPublished = handlers.onLocalTrackPublished;
    this.onParticipantConnected = handlers.onParticipantConnected;
    this.onParticipantDisconnected = handlers.onParticipantDisconnected;
    this.onDisconnected = handlers.onDisconnected;
  }
}
```

### Step 4: React Component Example

```jsx
// VideoCallComponent.jsx
import React, { useState, useEffect, useRef } from 'react';

const VideoCallComponent = ({ roomId, authManager }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [participants, setParticipants] = useState([]);
  const [isCameraOn, setIsCameraOn] = useState(true);
  const [isMicOn, setIsMicOn] = useState(true);
  const videoContainerRef = useRef(null);
  const videoCallManager = useRef(null);

  useEffect(() => {
    const roomService = new RoomService(authManager);
    videoCallManager.current = new VideoCallManager(roomService);
    
    // Setup event handlers
    videoCallManager.current.setEventHandlers({
      onTrackSubscribed: (element, track, participant) => {
        addVideoElement(element, participant, track.kind);
      },
      onTrackUnsubscribed: (track, participant) => {
        removeVideoElement(participant, track.kind);
      },
      onLocalTrackPublished: (element, track, participant) => {
        addVideoElement(element, participant, track.kind, true);
      },
      onParticipantConnected: (participant) => {
        console.log('Participant joined:', participant.identity);
      },
      onParticipantDisconnected: (participant) => {
        console.log('Participant left:', participant.identity);
      },
      onDisconnected: () => {
        setIsConnected(false);
        clearVideoContainer();
      }
    });

    return () => {
      if (videoCallManager.current) {
        videoCallManager.current.disconnect();
      }
    };
  }, [roomId]);

  const addVideoElement = (element, participant, trackKind, isLocal = false) => {
    const container = document.createElement('div');
    container.className = 'video-participant';
    container.id = `${participant.identity}-${trackKind}`;
    
    element.style.width = '100%';
    element.style.height = '200px';
    element.style.objectFit = 'cover';
    element.style.borderRadius = '8px';
    
    if (isLocal && trackKind === 'video') {
      element.style.transform = 'scaleX(-1)'; // Mirror local video
    }

    const label = document.createElement('div');
    label.textContent = `${isLocal ? 'You' : participant.identity} (${trackKind})`;
    label.style.textAlign = 'center';
    label.style.padding = '5px';
    label.style.background = 'rgba(0,0,0,0.7)';
    label.style.color = 'white';

    container.appendChild(element);
    container.appendChild(label);
    videoContainerRef.current?.appendChild(container);
  };

  const removeVideoElement = (participant, trackKind) => {
    const element = document.getElementById(`${participant.identity}-${trackKind}`);
    if (element) {
      element.remove();
    }
  };

  const clearVideoContainer = () => {
    if (videoContainerRef.current) {
      videoContainerRef.current.innerHTML = '';
    }
  };

  const handleJoinCall = async () => {
    try {
      await videoCallManager.current.joinVideoCall(roomId);
      setIsConnected(true);
    } catch (error) {
      console.error('Failed to join call:', error);
      alert('Failed to join call: ' + error.message);
    }
  };

  const handleLeaveCall = async () => {
    await videoCallManager.current.disconnect();
    setIsConnected(false);
    clearVideoContainer();
  };

  const handleToggleCamera = async () => {
    const newState = await videoCallManager.current.toggleCamera();
    setIsCameraOn(newState);
  };

  const handleToggleMicrophone = async () => {
    const newState = await videoCallManager.current.toggleMicrophone();
    setIsMicOn(newState);
  };

  return (
    <div className="video-call-container">
      <div className="controls">
        {!isConnected ? (
          <button onClick={handleJoinCall} className="join-btn">
            Join Call
          </button>
        ) : (
          <>
            <button onClick={handleLeaveCall} className="leave-btn">
              Leave Call
            </button>
            <button 
              onClick={handleToggleCamera}
              className={isCameraOn ? 'camera-on' : 'camera-off'}
            >
              {isCameraOn ? '📹 Camera On' : '📹 Camera Off'}
            </button>
            <button 
              onClick={handleToggleMicrophone}
              className={isMicOn ? 'mic-on' : 'mic-off'}
            >
              {isMicOn ? '🎤 Mic On' : '🎤 Mic Off'}
            </button>
          </>
        )}
      </div>
      
      <div 
        ref={videoContainerRef}
        className="video-container"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '10px',
          marginTop: '20px'
        }}
      >
        {!isConnected && (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            Click "Join Call" to start the video call
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoCallComponent;
```

---

## 📚 API Reference

### Authentication Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/auth/register` | POST | Register new user | No |
| `/auth/login` | POST | User login | No |
| `/auth/me` | GET | Get current user | Yes |

### Room Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/rooms/` | POST | Create room | Yes |
| `/rooms/` | GET | List rooms | Yes |
| `/rooms/{id}` | GET | Get room details | Yes |
| `/rooms/{id}/join` | POST | Join room (get LiveKit token) | Yes |
| `/rooms/{id}/leave` | POST | Leave room | Yes |
| `/rooms/{id}/participants` | GET | Get room participants | Yes |
| `/rooms/{id}` | DELETE | Delete room (creator only) | Yes |

### User Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/users/` | GET | List users | Yes |
| `/users/{id}` | GET | Get user details | Yes |

---

## ⚠️ Error Handling

### Common Error Responses

```javascript
// Authentication errors
{
  "detail": "Could not validate credentials"
} // Status: 401

// Permission errors
{
  "detail": "Only the room creator can delete the room"
} // Status: 403

// Not found errors
{
  "detail": "Room not found"
} // Status: 404

// Validation errors
{
  "detail": "Email already registered"
} // Status: 400
```

### Frontend Error Handling

```javascript
async function handleApiCall(apiCall) {
  try {
    const response = await apiCall();
    return response;
  } catch (error) {
    if (error.message.includes('401')) {
      // Token expired or invalid
      authManager.logout();
      window.location.href = '/login';
    } else if (error.message.includes('403')) {
      // Permission denied
      alert('You do not have permission to perform this action');
    } else if (error.message.includes('404')) {
      // Resource not found
      alert('The requested resource was not found');
    } else {
      // Generic error
      console.error('API Error:', error);
      alert('An error occurred. Please try again.');
    }
    throw error;
  }
}
```

---

## 🧪 Testing

### Test Users
The backend setup script creates a default test user:
```
Username: testuser
Password: testpassword123
Email: test@example.com
```

### API Testing Commands

```bash
# Register user
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "test", "email": "test@example.com", "password": "test123", "full_name": "Test User"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=test&password=test123"

# Create room (replace TOKEN)
curl -X POST "http://localhost:8000/rooms/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"name": "Test Room", "description": "Test", "max_participants": 10}'

# Join room (replace TOKEN and ROOM_ID)
curl -X POST "http://localhost:8000/rooms/1/join" \
     -H "Authorization: Bearer TOKEN"
```

### Frontend Testing Checklist

- [ ] User registration works
- [ ] User login works
- [ ] JWT token is stored and used correctly
- [ ] Room creation works
- [ ] Room listing shows correct data
- [ ] Joining room returns valid LiveKit token
- [ ] Video call connects successfully
- [ ] Camera/microphone controls work
- [ ] Multiple participants can join
- [ ] Participants can leave room
- [ ] Error handling works for all scenarios

---

## 🚀 Deployment Considerations

### Environment Variables

```javascript
// config.js
const config = {
  API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  LIVEKIT_URL: process.env.REACT_APP_LIVEKIT_URL || 'wss://osadho-m62vhfz7.livekit.cloud',
};
```

### CORS Configuration
Ensure your backend allows your frontend domain:
```python
# In backend main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Security Best Practices

1. **Token Storage**: Use secure storage (httpOnly cookies in production)
2. **HTTPS**: Always use HTTPS in production
3. **Token Refresh**: Implement token refresh mechanism
4. **Input Validation**: Validate all user inputs
5. **Error Messages**: Don't expose sensitive information in error messages

### Performance Optimization

1. **Video Quality**: Implement adaptive video quality based on network
2. **Connection Recovery**: Handle network disconnections gracefully
3. **Resource Cleanup**: Always clean up video tracks and connections
4. **Batch Updates**: Batch participant updates to avoid UI flickering

---

## 📞 Support

### Backend Documentation
- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### LiveKit Documentation
- [LiveKit Client SDK](https://docs.livekit.io/realtime/client/web/)
- [LiveKit React Components](https://docs.livekit.io/realtime/client/react/)

### Common Issues

1. **Token Expiration**: Tokens expire after 30 minutes by default
2. **CORS Errors**: Check backend CORS configuration
3. **Media Permissions**: Ensure browser has camera/microphone permissions
4. **Network Issues**: Handle poor network conditions gracefully

---

## 📝 Notes

- JWT tokens expire after 30 minutes (configurable)
- LiveKit tokens are room-specific and participant-specific
- Rooms are automatically created in LiveKit when first participant joins
- The backend tracks participants separately from LiveKit for persistence
- All API endpoints except login/register require authentication

This guide provides everything your frontend team needs to integrate with the LiveKit video calling backend. For any questions or issues, refer to the API documentation at `/docs` or contact the backend team.
