#!/usr/bin/env python3
"""
Debug script to test czterykola field specifically
"""

import requests
import json

# Configuration
BASE_URL = "https://fhu-vehicles.preview.emergentagent.com/api"
ADMIN_PATH = "admin-X9T4G7QJ2MZP8L1W3R5C6VDHY"
ADMIN_PASSWORD = "FHUfranko!%Nbzw"

def main():
    session = requests.Session()
    
    # Login first
    print("🔐 Logging in...")
    login_url = f"{BASE_URL}/{ADMIN_PATH}"
    login_data = {"password": ADMIN_PASSWORD}
    response = session.post(login_url, json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Get a bus to test with
    print("\n🚌 Getting test bus...")
    response = requests.get(f"{BASE_URL}/ogloszenia")
    if response.status_code != 200:
        print(f"❌ Failed to get buses: {response.status_code}")
        return
    
    buses = response.json()
    if not buses:
        print("❌ No buses available")
        return
    
    test_bus_id = buses[0]['id']
    print(f"✅ Using bus ID: {test_bus_id}")
    
    # Get current state
    print(f"\n📊 Current bus state:")
    response = requests.get(f"{BASE_URL}/ogloszenia/{test_bus_id}")
    if response.status_code == 200:
        bus_data = response.json()
        print(f"   gwarancja: {bus_data.get('gwarancja', 'N/A')}")
        print(f"   czterykola: {bus_data.get('czterykola', 'N/A')}")
        print(f"   sold: {bus_data.get('sold', 'N/A')}")
        print(f"   reserved: {bus_data.get('reserved', 'N/A')}")
    
    # Test 1: Set czterykola=true only
    print(f"\n🔧 Test 1: Setting czterykola=true only...")
    update_data = {'czterykola': True}
    response = session.put(f"{BASE_URL}/ogloszenia/{test_bus_id}", json=update_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        updated_bus = response.json()
        print(f"   Result - czterykola: {updated_bus.get('czterykola', 'N/A')}")
        print(f"   Result - gwarancja: {updated_bus.get('gwarancja', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
    
    # Test 2: Set both czterykola=true and gwarancja=false
    print(f"\n🔧 Test 2: Setting czterykola=true and gwarancja=false...")
    update_data = {'czterykola': True, 'gwarancja': False}
    response = session.put(f"{BASE_URL}/ogloszenia/{test_bus_id}", json=update_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        updated_bus = response.json()
        print(f"   Result - czterykola: {updated_bus.get('czterykola', 'N/A')}")
        print(f"   Result - gwarancja: {updated_bus.get('gwarancja', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
    
    # Test 3: Check final state
    print(f"\n📊 Final bus state:")
    response = requests.get(f"{BASE_URL}/ogloszenia/{test_bus_id}")
    if response.status_code == 200:
        bus_data = response.json()
        print(f"   gwarancja: {bus_data.get('gwarancja', 'N/A')}")
        print(f"   czterykola: {bus_data.get('czterykola', 'N/A')}")
        print(f"   sold: {bus_data.get('sold', 'N/A')}")
        print(f"   reserved: {bus_data.get('reserved', 'N/A')}")
    
    # Test 4: Reset to clean state
    print(f"\n🧹 Resetting to clean state...")
    update_data = {'czterykola': False, 'gwarancja': False}
    response = session.put(f"{BASE_URL}/ogloszenia/{test_bus_id}", json=update_data)
    print(f"   Status: {response.status_code}")

if __name__ == "__main__":
    main()