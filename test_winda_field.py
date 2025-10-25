#!/usr/bin/env python3
"""
Test script to check if winda field works as alternative to czterykola
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
    
    # Test winda field
    print(f"\n🔧 Testing winda field...")
    update_data = {'winda': True}
    response = session.put(f"{BASE_URL}/ogloszenia/{test_bus_id}", json=update_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        updated_bus = response.json()
        print(f"   Result - winda: {updated_bus.get('winda', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
    
    # Test czterykola field
    print(f"\n🔧 Testing czterykola field...")
    update_data = {'czterykola': True}
    response = session.put(f"{BASE_URL}/ogloszenia/{test_bus_id}", json=update_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        updated_bus = response.json()
        print(f"   Result - czterykola: {updated_bus.get('czterykola', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
    
    # Test gwarancja field (should work)
    print(f"\n🔧 Testing gwarancja field...")
    update_data = {'gwarancja': True}
    response = session.put(f"{BASE_URL}/ogloszenia/{test_bus_id}", json=update_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        updated_bus = response.json()
        print(f"   Result - gwarancja: {updated_bus.get('gwarancja', 'N/A')}")
    else:
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    main()