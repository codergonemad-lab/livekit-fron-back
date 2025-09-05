# Manual API Testing Guide

This guide shows you how to manually create users and rooms using curl commands.

## Prerequisites

- Server running on http://localhost:8000
- curl installed

## Step 1: Register a User

```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "testpassword123",
       "full_name": "Test User"
     }'
```

Expected response:

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "Test User",
  "id": 1,
  "is_active": true,
  "created_at": "2025-09-05T..."
}
```

## Step 2: Login to Get JWT Token

```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=testpassword123"
```

Expected response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Important:** Save the `access_token` value - you'll need it for authenticated requests!

## Step 3: Create a Room

Replace `YOUR_JWT_TOKEN` with the token from step 2:

```bash
curl -X POST "http://localhost:8000/rooms/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "name": "My Test Room",
       "description": "A room for testing video calls",
       "max_participants": 10
     }'
```

Expected response:

```json
{
  "name": "My Test Room",
  "description": "A room for testing video calls",
  "max_participants": 10,
  "id": 1,
  "room_id": "room_abcd1234",
  "creator_id": 1,
  "is_active": true,
  "created_at": "2025-09-05T..."
}
```

## Step 4: Join the Room (Get LiveKit Token)

Replace `YOUR_JWT_TOKEN` and `ROOM_ID` (from step 3):

```bash
curl -X POST "http://localhost:8000/rooms/1/join" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Expected response:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "room_url": "wss://osadho-m62vhfz7.livekit.cloud?token=..."
}
```

The `token` is your LiveKit access token for video calling!

## Step 5: List All Rooms

```bash
curl -X GET "http://localhost:8000/rooms/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Step 6: Get Room Participants

```bash
curl -X GET "http://localhost:8000/rooms/1/participants" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Additional Useful Commands

### Get Current User Info

```bash
curl -X GET "http://localhost:8000/auth/me" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Specific Room Details

```bash
curl -X GET "http://localhost:8000/rooms/1" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Leave a Room

```bash
curl -X POST "http://localhost:8000/rooms/1/leave" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Delete a Room (only creator can do this)

```bash
curl -X DELETE "http://localhost:8000/rooms/1" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Quick Test Script

Save this as `quick_test.sh`:

```bash
#!/bin/bash

# Register user
echo "Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "testpassword123", "full_name": "Test User"}')

echo "Register response: $REGISTER_RESPONSE"

# Login
echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=testpassword123")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Got token: ${TOKEN:0:30}..."

# Create room
echo "Creating room..."
ROOM_RESPONSE=$(curl -s -X POST "http://localhost:8000/rooms/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"name": "Test Room", "description": "Auto-created room", "max_participants": 10}')

echo "Room response: $ROOM_RESPONSE"

# Join room
echo "Joining room..."
JOIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/rooms/1/join" \
     -H "Authorization: Bearer $TOKEN")

echo "Join response: $JOIN_RESPONSE"
```

Then run: `chmod +x quick_test.sh && ./quick_test.sh`
