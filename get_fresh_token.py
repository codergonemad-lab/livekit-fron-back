#!/usr/bin/env python3
"""
Quick script to get a fresh LiveKit token for testing
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def get_fresh_token():
    print("🔄 Getting fresh LiveKit token...")
    
    # Login as testuser
    login_response = requests.post(f"{BASE_URL}/auth/login", 
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="username=testuser&password=testpassword123"
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed:", login_response.text)
        return
    
    jwt_token = login_response.json()["access_token"]
    print(f"✅ Got JWT token: {jwt_token[:30]}...")
    
    # Join room 1 to get LiveKit token
    join_response = requests.post(f"{BASE_URL}/rooms/1/join",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    
    if join_response.status_code != 200:
        print("❌ Failed to join room:", join_response.text)
        return
    
    join_data = join_response.json()
    print("\n🎉 Fresh tokens ready!")
    print("=" * 50)
    print(f"JWT Token: {jwt_token}")
    print(f"LiveKit Token: {join_data['token']}")
    print(f"Room URL: {join_data['room_url']}")
    print("=" * 50)
    
    # Update the HTML file with fresh token
    html_content = f"""
    // Replace this in your HTML file:
    const LIVEKIT_TOKEN = '{join_data['token']}';
    """
    
    print("\n📝 Copy this token to your HTML file:")
    print(html_content)
    
    return join_data

if __name__ == "__main__":
    get_fresh_token()
