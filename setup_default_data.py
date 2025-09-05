#!/usr/bin/env python3
"""
Script to create a default user and room for testing the LiveKit backend.
This script will:
1. Register a default user
2. Login to get a JWT token
3. Create a default room
4. Show you how to join the room
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
DEFAULT_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
}
DEFAULT_ROOM = {
    "name": "Test Video Room",
    "description": "A default room for testing video calls",
    "max_participants": 10
}

def make_request(method, endpoint, data=None, token=None):
    """Make HTTP request with error handling."""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if endpoint == "/auth/login":
                # Login endpoint expects form data
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                response = requests.post(url, data=data, headers=headers)
            else:
                response = requests.post(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
            
        return response
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to the server. Make sure it's running on http://localhost:8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error making request: {e}")
        sys.exit(1)

def register_user():
    """Register a new user."""
    print("📝 Registering default user...")
    response = make_request("POST", "/auth/register", DEFAULT_USER)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ User registered successfully!")
        print(f"   Username: {user_data['username']}")
        print(f"   Email: {user_data['email']}")
        print(f"   User ID: {user_data['id']}")
        return user_data
    elif response.status_code == 400:
        error = response.json()
        if "already" in error.get("detail", "").lower():
            print(f"ℹ️  User already exists: {error['detail']}")
            return None
        else:
            print(f"❌ Registration failed: {error['detail']}")
            sys.exit(1)
    else:
        print(f"❌ Registration failed with status {response.status_code}")
        print(response.text)
        sys.exit(1)

def login_user():
    """Login and get JWT token."""
    print("\n🔐 Logging in...")
    login_data = {
        "username": DEFAULT_USER["username"],
        "password": DEFAULT_USER["password"]
    }
    
    response = make_request("POST", "/auth/login", login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ Login successful!")
        print(f"   Token type: {token_data['token_type']}")
        return token_data["access_token"]
    else:
        error = response.json()
        print(f"❌ Login failed: {error['detail']}")
        sys.exit(1)

def create_room(token):
    """Create a default room."""
    print("\n🏠 Creating default room...")
    response = make_request("POST", "/rooms/", DEFAULT_ROOM, token)
    
    if response.status_code == 200:
        room_data = response.json()
        print("✅ Room created successfully!")
        print(f"   Room ID: {room_data['id']}")
        print(f"   Room Name: {room_data['name']}")
        print(f"   LiveKit Room ID: {room_data['room_id']}")
        print(f"   Creator ID: {room_data['creator_id']}")
        return room_data
    else:
        error = response.json()
        print(f"❌ Room creation failed: {error['detail']}")
        sys.exit(1)

def join_room(token, room_id):
    """Join the room and get LiveKit token."""
    print(f"\n🎬 Joining room {room_id}...")
    response = make_request("POST", f"/rooms/{room_id}/join", None, token)
    
    if response.status_code == 200:
        join_data = response.json()
        print("✅ Successfully joined room!")
        print(f"   LiveKit Token: {join_data['token'][:50]}...")
        print(f"   Room URL: {join_data['room_url'][:80]}...")
        return join_data
    else:
        error = response.json()
        print(f"❌ Failed to join room: {error['detail']}")
        sys.exit(1)

def list_rooms(token):
    """List all available rooms."""
    print("\n📋 Listing all rooms...")
    response = make_request("GET", "/rooms/", None, token)
    
    if response.status_code == 200:
        rooms = response.json()
        print(f"✅ Found {len(rooms)} room(s):")
        for room in rooms:
            print(f"   • Room {room['id']}: {room['name']} ({room['participants_count']} participants)")
        return rooms
    else:
        print(f"❌ Failed to list rooms: {response.text}")
        return []

def main():
    """Main function to set up default user and room."""
    print("🚀 LiveKit Backend Setup Script")
    print("=" * 40)
    
    # Step 1: Register user
    user_data = register_user()
    
    # Step 2: Login
    token = login_user()
    
    # Step 3: Create room
    room_data = create_room(token)
    
    # Step 4: Join room (to get LiveKit token)
    join_data = join_room(token, room_data["id"])
    
    # Step 5: List all rooms
    list_rooms(token)
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("\n📝 Summary:")
    print(f"   • User: {DEFAULT_USER['username']} (ID: {room_data['creator_id']})")
    print(f"   • Room: {room_data['name']} (ID: {room_data['id']})")
    print(f"   • JWT Token: {token[:30]}...")
    print(f"   • LiveKit Token: {join_data['token'][:30]}...")
    
    print("\n🔗 API Endpoints to try:")
    print(f"   • API Docs: {BASE_URL}/docs")
    print(f"   • Get user info: GET {BASE_URL}/auth/me")
    print(f"   • List rooms: GET {BASE_URL}/rooms/")
    print(f"   • Room details: GET {BASE_URL}/rooms/{room_data['id']}")
    
    print("\n💡 Next steps:")
    print("   1. Visit http://localhost:8000/docs to explore the API")
    print("   2. Use the LiveKit token in your video calling frontend")
    print("   3. Create more users and rooms as needed")
    
    # Save tokens to file for easy access
    with open("tokens.json", "w") as f:
        json.dump({
            "jwt_token": token,
            "livekit_token": join_data["token"],
            "room_id": room_data["id"],
            "room_name": room_data["name"],
            "user": {
                "username": DEFAULT_USER["username"],
                "id": room_data["creator_id"]
            },
            "created_at": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n💾 Tokens saved to tokens.json for future use")

if __name__ == "__main__":
    main()
