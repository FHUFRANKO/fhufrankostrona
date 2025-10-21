#!/usr/bin/env python3
"""
Simulate the frontend behavior to identify the exact issue
"""

import requests
import json

BASE_URL = "https://busfleet-mgmt.preview.emergentagent.com/api"

def simulate_frontend_issue():
    """Simulate the exact frontend behavior that's causing 401 errors"""
    
    print("🎭 Simulating Frontend Behavior...")
    print("=" * 50)
    
    # Scenario 1: User directly accesses /admin without logging in first
    print("\n1. Simulating direct access to /admin (no login):")
    print("   This is what happens when AdminPanel useEffect runs...")
    
    # Create a fresh session (no cookies)
    fresh_session = requests.Session()
    
    try:
        # This simulates the fetchOpinions() call in useEffect
        response = fresh_session.get(f"{BASE_URL}/opinie")
        print(f"   GET /api/opinie Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print("   ❌ This is the 401 error users see in admin panel!")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    
    # Scenario 2: Proper login flow
    print("\n2. Simulating proper login flow:")
    
    # Step 1: User goes to login page and submits password
    login_session = requests.Session()
    login_data = {"password": "ZmienMnieTeraz123!"}
    
    try:
        login_response = login_session.post(f"{BASE_URL}/admin-moj-tajny-panel-82374", json=login_data)
        print(f"   Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("   ✅ Login successful, cookie set")
            
            # Step 2: Now try to fetch opinions (this should work)
            opinions_response = login_session.get(f"{BASE_URL}/opinie")
            print(f"   GET /api/opinie Status: {opinions_response.status_code}")
            
            if opinions_response.status_code == 200:
                opinions = opinions_response.json()
                print(f"   ✅ Success! Retrieved {len(opinions)} opinions")
            else:
                print(f"   ❌ Still failed: {opinions_response.text}")
        else:
            print(f"   ❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"   Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🔍 DIAGNOSIS:")
    print("The issue is that AdminPanel.jsx calls fetchOpinions() in useEffect")
    print("BEFORE the user has logged in and received the admin session cookie.")
    print("This causes the 401 error that users see in the admin panel.")
    print("\nSOLUTION NEEDED:")
    print("- Add authentication check before calling admin endpoints")
    print("- Or delay the fetchOpinions() call until after login")
    print("- Or handle 401 errors gracefully in the frontend")

if __name__ == "__main__":
    simulate_frontend_issue()