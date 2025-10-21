#!/usr/bin/env python3
"""
Test cookie authentication specifically for the opinions endpoint issue
"""

import requests
import json

BASE_URL = "https://busfleet-mgmt.preview.emergentagent.com/api"
ADMIN_PATH = "admin-moj-tajny-panel-82374"
ADMIN_PASSWORD = "ZmienMnieTeraz123!"

def test_cookie_auth_issue():
    """Test the specific cookie authentication issue with opinions endpoint"""
    
    print("🔍 Testing Cookie Authentication Issue...")
    print("=" * 50)
    
    # Test 1: Direct request without authentication (should fail)
    print("\n1. Testing GET /api/opinie without authentication:")
    try:
        response = requests.get(f"{BASE_URL}/opinie")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    
    # Test 2: Login and get cookie
    print("\n2. Testing admin login to get cookie:")
    session = requests.Session()
    try:
        login_response = session.post(f"{BASE_URL}/{ADMIN_PATH}", json={"password": ADMIN_PASSWORD})
        print(f"   Login Status: {login_response.status_code}")
        cookies = session.cookies.get_dict()
        print(f"   Cookies received: {cookies}")
        
        if 'admin_session' in cookies:
            print(f"   Admin session cookie: {cookies['admin_session'][:30]}...")
            
            # Test 3: Use session with cookie for opinions endpoint
            print("\n3. Testing GET /api/opinie with session cookie:")
            opinions_response = session.get(f"{BASE_URL}/opinie")
            print(f"   Status: {opinions_response.status_code}")
            if opinions_response.status_code == 200:
                opinions = opinions_response.json()
                print(f"   Success! Retrieved {len(opinions)} opinions")
            else:
                print(f"   Failed! Response: {opinions_response.text[:200]}...")
            
            # Test 4: Manual cookie test (simulate frontend behavior)
            print("\n4. Testing with manual cookie header (simulating frontend):")
            manual_session = requests.Session()
            manual_session.cookies.set('admin_session', cookies['admin_session'])
            
            manual_response = manual_session.get(f"{BASE_URL}/opinie")
            print(f"   Status: {manual_response.status_code}")
            if manual_response.status_code == 200:
                opinions = manual_response.json()
                print(f"   Success! Retrieved {len(opinions)} opinions")
            else:
                print(f"   Failed! Response: {manual_response.text[:200]}...")
                
            # Test 5: Check cookie domain and path issues
            print("\n5. Cookie details analysis:")
            for cookie in session.cookies:
                print(f"   Cookie: {cookie.name}")
                print(f"   Value: {cookie.value[:30]}...")
                print(f"   Domain: {cookie.domain}")
                print(f"   Path: {cookie.path}")
                print(f"   Secure: {cookie.secure}")
                print(f"   HttpOnly: {cookie.has_nonstandard_attr('HttpOnly')}")
                
        else:
            print("   No admin_session cookie received!")
            
    except Exception as e:
        print(f"   Exception: {str(e)}")

if __name__ == "__main__":
    test_cookie_auth_issue()