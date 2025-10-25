#!/usr/bin/env python3
"""
FHU Franko Bus Dealership Backend API Test Suite
Tests all endpoints with proper authentication flow
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
import uuid

# Configuration
BASE_URL = "https://fhu-vehicles.preview.emergentagent.com/api"
ADMIN_PATH = "admin-X9T4G7QJ2MZP8L1W3R5C6VDHY"
ADMIN_PASSWORD = "FHUfranko!%Nbzw"

class BusAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_authenticated = False
        self.test_results = []
        self.created_bus_id = None
        self.created_opinion_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def test_admin_authentication(self) -> bool:
        """Test admin login and get session cookie"""
        print("\n🔐 Testing Admin Authentication...")
        
        try:
            # Test admin login
            login_url = f"{BASE_URL}/{ADMIN_PATH}"
            login_data = {"password": ADMIN_PASSWORD}
            
            response = self.session.post(login_url, json=login_data)
            
            if response.status_code == 200:
                # Check if we got the admin session cookie
                cookies = self.session.cookies.get_dict()
                if 'admin_session' in cookies:
                    self.admin_authenticated = True
                    self.log_test("Admin Authentication", True, f"Cookie received: {cookies['admin_session'][:20]}...")
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No admin_session cookie received")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_public_endpoints(self):
        """Test all public endpoints that should work without authentication"""
        print("\n🌐 Testing Public Endpoints...")
        
        # Test GET /api/ogloszenia (get all buses)
        try:
            response = requests.get(f"{BASE_URL}/ogloszenia")
            if response.status_code == 200:
                buses = response.json()
                self.log_test("GET /api/ogloszenia (public)", True, f"Retrieved {len(buses)} buses")
                
                # Store first bus ID for single bus test
                if buses and len(buses) > 0:
                    first_bus_id = buses[0].get('id')
                    if first_bus_id:
                        # Test GET single bus
                        single_response = requests.get(f"{BASE_URL}/ogloszenia/{first_bus_id}")
                        if single_response.status_code == 200:
                            bus_data = single_response.json()
                            self.log_test("GET /api/ogloszenia/{bus_id} (public)", True, f"Retrieved bus: {bus_data.get('marka', 'Unknown')} {bus_data.get('model', 'Unknown')}")
                        else:
                            self.log_test("GET /api/ogloszenia/{bus_id} (public)", False, f"Status: {single_response.status_code}")
                    else:
                        self.log_test("GET /api/ogloszenia/{bus_id} (public)", False, "No bus ID found in response")
                else:
                    self.log_test("GET /api/ogloszenia/{bus_id} (public)", False, "No buses available to test single bus endpoint")
            else:
                self.log_test("GET /api/ogloszenia (public)", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("GET /api/ogloszenia (public)", False, f"Exception: {str(e)}")
        
        # Test GET /api/opinie/public (get public opinions)
        try:
            response = requests.get(f"{BASE_URL}/opinie/public")
            if response.status_code == 200:
                opinions = response.json()
                self.log_test("GET /api/opinie/public", True, f"Retrieved {len(opinions)} public opinions")
            else:
                self.log_test("GET /api/opinie/public", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("GET /api/opinie/public", False, f"Exception: {str(e)}")
        
        # Test GET /api/stats (get statistics)
        try:
            response = requests.get(f"{BASE_URL}/stats")
            if response.status_code == 200:
                stats = response.json()
                self.log_test("GET /api/stats", True, f"Stats: {stats}")
            else:
                self.log_test("GET /api/stats", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("GET /api/stats", False, f"Exception: {str(e)}")
    
    def test_admin_bus_endpoints(self):
        """Test admin-only bus endpoints"""
        print("\n🚌 Testing Admin Bus Endpoints...")
        
        if not self.admin_authenticated:
            self.log_test("Admin Bus Endpoints", False, "Admin authentication required")
            return
        
        # Test POST /api/ogloszenia (create bus)
        bus_data = {
            "marka": "Mercedes-Benz",
            "model": "Sprinter 516 CDI",
            "rok": 2022,
            "przebieg": 45000,
            "paliwo": "Diesel",
            "skrzynia": "Manualna",
            "naped": "Przedni",
            "cenaBrutto": 185000,
            "cenaNetto": 150407,
            "vat": True,
            "typNadwozia": "Furgon",
            "moc": 163,
            "kubatura": 2143,
            "normaSpalania": "7.8 l/100km",
            "normaEmisji": "Euro 6",
            "dmcKategoria": "do 3.5t",
            "ladownosc": 1500,
            "wymiarL": "L2",
            "wymiarH": "H2",
            "pojemnoscSkrzyni": 11,
            "winda": False,
            "hak": True,
            "czterykola": False,
            "klimatyzacja": True,
            "tempomat": True,
            "kamera": True,
            "czujnikiParkowania": True,
            "wyrozniowane": False,
            "nowosc": True,
            "flotowy": False,
            "gwarancja": True,
            "kolor": "Biały",
            "pierwszaRejestracja": "2022-03-15",
            "miasto": "Warszawa",
            "opis": "Doskonały stan techniczny, serwisowany w ASO Mercedes-Benz. Idealny do transportu kurierskiego.",
            "zdjecia": []
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/ogloszenia", json=bus_data)
            if response.status_code == 200:
                created_bus = response.json()
                self.created_bus_id = created_bus.get('id')
                self.log_test("POST /api/ogloszenia (create bus)", True, f"Created bus ID: {self.created_bus_id}")
                
                # Test PUT /api/ogloszenia/{bus_id} (update bus)
                if self.created_bus_id:
                    update_data = {
                        "przebieg": 46000,
                        "cenaBrutto": 180000,
                        "opis": "Zaktualizowany opis - doskonały stan, niski przebieg"
                    }
                    
                    update_response = self.session.put(f"{BASE_URL}/ogloszenia/{self.created_bus_id}", json=update_data)
                    if update_response.status_code == 200:
                        updated_bus = update_response.json()
                        self.log_test("PUT /api/ogloszenia/{bus_id} (update bus)", True, f"Updated przebieg: {updated_bus.get('przebieg')}")
                    else:
                        self.log_test("PUT /api/ogloszenia/{bus_id} (update bus)", False, f"Status: {update_response.status_code}")
            else:
                self.log_test("POST /api/ogloszenia (create bus)", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("POST /api/ogloszenia (create bus)", False, f"Exception: {str(e)}")
    
    def test_admin_opinion_endpoints(self):
        """Test admin-only opinion endpoints - this is the problematic area"""
        print("\n💬 Testing Admin Opinion Endpoints...")
        
        if not self.admin_authenticated:
            self.log_test("Admin Opinion Endpoints", False, "Admin authentication required")
            return
        
        # Test GET /api/opinie (get all opinions for admin) - This is the failing endpoint
        try:
            response = self.session.get(f"{BASE_URL}/opinie")
            if response.status_code == 200:
                opinions = response.json()
                self.log_test("GET /api/opinie (admin)", True, f"Retrieved {len(opinions)} opinions for admin")
            else:
                self.log_test("GET /api/opinie (admin)", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("GET /api/opinie (admin)", False, f"Exception: {str(e)}")
        
        # Test POST /api/opinie (create opinion)
        opinion_data = {
            "imie": "Marek Kowalski",
            "typDzialalnosci": "Firma kurierska",
            "komentarz": "Świetna obsługa i profesjonalne doradztwo. Zakupiony Mercedes Sprinter spełnia wszystkie nasze oczekiwania. Polecam FHU Franko!",
            "ocena": 5,
            "zakupionyPojazd": "Mercedes-Benz Sprinter 516 CDI",
            "wyswietlaj": True
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/opinie", json=opinion_data)
            if response.status_code == 200:
                created_opinion = response.json()
                self.created_opinion_id = created_opinion.get('id')
                self.log_test("POST /api/opinie (create opinion)", True, f"Created opinion ID: {self.created_opinion_id}")
                
                # Test PUT /api/opinie/{opinion_id} (update opinion)
                if self.created_opinion_id:
                    update_data = {
                        "komentarz": "Zaktualizowany komentarz - nadal bardzo zadowolony z zakupu!",
                        "ocena": 5
                    }
                    
                    update_response = self.session.put(f"{BASE_URL}/opinie/{self.created_opinion_id}", json=update_data)
                    if update_response.status_code == 200:
                        updated_opinion = update_response.json()
                        self.log_test("PUT /api/opinie/{opinion_id} (update opinion)", True, f"Updated opinion")
                    else:
                        self.log_test("PUT /api/opinie/{opinion_id} (update opinion)", False, f"Status: {update_response.status_code}")
            else:
                self.log_test("POST /api/opinie (create opinion)", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("POST /api/opinie (create opinion)", False, f"Exception: {str(e)}")
    
    def test_rezerwacja_toggle_endpoints(self):
        """Test REZERWACJA feature toggle endpoints (sold/reserved mutual exclusivity)"""
        print("\n🔄 Testing REZERWACJA Toggle Endpoints...")
        
        if not self.admin_authenticated:
            self.log_test("REZERWACJA Toggle Endpoints", False, "Admin authentication required")
            return
        
        # First, get a bus to test with
        test_bus_id = None
        try:
            # Get all buses to find one to test with
            response = requests.get(f"{BASE_URL}/ogloszenia")
            if response.status_code == 200:
                buses = response.json()
                if buses and len(buses) > 0:
                    test_bus_id = buses[0].get('id')
                    self.log_test("Get test bus for REZERWACJA", True, f"Using bus ID: {test_bus_id}")
                else:
                    self.log_test("Get test bus for REZERWACJA", False, "No buses available for testing")
                    return
            else:
                self.log_test("Get buses for REZERWACJA test", False, f"Status: {response.status_code}")
                return
        except Exception as e:
            self.log_test("Get buses for REZERWACJA test", False, f"Exception: {str(e)}")
            return
        
        if not test_bus_id:
            self.log_test("REZERWACJA Toggle Tests", False, "No test bus available")
            return
        
        # Test 1: Toggle sold status (should work - uses gwarancja field)
        try:
            response = self.session.post(f"{BASE_URL}/ogloszenia/{test_bus_id}/toggle-sold")
            if response.status_code == 200:
                result = response.json()
                expected_keys = ['success', 'sold', 'reserved']
                if all(key in result for key in expected_keys):
                    self.log_test("POST /api/ogloszenia/{id}/toggle-sold", True, f"✅ WORKS: Sold: {result['sold']}, Reserved: {result['reserved']}")
                else:
                    self.log_test("POST /api/ogloszenia/{id}/toggle-sold", False, f"Missing expected keys in response: {result}")
            else:
                self.log_test("POST /api/ogloszenia/{id}/toggle-sold", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("POST /api/ogloszenia/{id}/toggle-sold", False, f"Exception: {str(e)}")
        
        # Test 2: Toggle reserved status (CRITICAL TEST - uses czterykola field)
        try:
            response = self.session.post(f"{BASE_URL}/ogloszenia/{test_bus_id}/toggle-reserved")
            if response.status_code == 200:
                result = response.json()
                expected_keys = ['success', 'sold', 'reserved']
                if all(key in result for key in expected_keys):
                    self.log_test("POST /api/ogloszenia/{id}/toggle-reserved", True, f"✅ FIXED: Reserved: {result['reserved']}, Sold: {result['sold']}")
                else:
                    self.log_test("POST /api/ogloszenia/{id}/toggle-reserved", False, f"Missing expected keys in response: {result}")
            else:
                # This is the critical failure we're testing for
                if "czterykola" in response.text and "PGRST204" in response.text:
                    self.log_test("POST /api/ogloszenia/{id}/toggle-reserved", False, f"❌ SCHEMA CACHE ISSUE: {response.text}")
                else:
                    self.log_test("POST /api/ogloszenia/{id}/toggle-reserved", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("POST /api/ogloszenia/{id}/toggle-reserved", False, f"Exception: {str(e)}")
        
        # Test 3: Verify regular PUT works with czterykola (to confirm field exists)
        try:
            update_data = {'czterykola': True}
            response = self.session.put(f"{BASE_URL}/ogloszenia/{test_bus_id}", json=update_data)
            if response.status_code == 200:
                self.log_test("PUT /api/ogloszenia/{id} with czterykola field", True, "✅ Regular PUT with czterykola works - field exists in DB")
            else:
                self.log_test("PUT /api/ogloszenia/{id} with czterykola field", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("PUT /api/ogloszenia/{id} with czterykola field", False, f"Exception: {str(e)}")
        
        # Test 4: Verify regular PUT works with winda (for comparison)
        try:
            update_data = {'winda': True}
            response = self.session.put(f"{BASE_URL}/ogloszenia/{test_bus_id}", json=update_data)
            if response.status_code == 200:
                self.log_test("PUT /api/ogloszenia/{id} with winda field", True, "✅ Regular PUT with winda works - field exists in DB")
            else:
                self.log_test("PUT /api/ogloszenia/{id} with winda field", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("PUT /api/ogloszenia/{id} with winda field", False, f"Exception: {str(e)}")
        
        # Test 5: Verify field mapping in GET endpoints (gwarancja → sold, czterykola → reserved)
        try:
            response = requests.get(f"{BASE_URL}/ogloszenia/{test_bus_id}")
            if response.status_code == 200:
                bus_data = response.json()
                if 'sold' in bus_data and 'reserved' in bus_data:
                    self.log_test("GET /api/ogloszenia/{id} (field mapping)", True, f"✅ Field mapping works: sold={bus_data['sold']}, reserved={bus_data['reserved']}")
                else:
                    self.log_test("GET /api/ogloszenia/{id} (field mapping)", False, f"Missing sold/reserved fields in response")
            else:
                self.log_test("GET /api/ogloszenia/{id} (field mapping)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/ogloszenia/{id} (field mapping)", False, f"Exception: {str(e)}")
        
        # Test 6: Verify field mapping in GET all buses
        try:
            response = requests.get(f"{BASE_URL}/ogloszenia")
            if response.status_code == 200:
                buses = response.json()
                if buses and len(buses) > 0:
                    all_have_fields = all('sold' in bus and 'reserved' in bus for bus in buses)
                    if all_have_fields:
                        self.log_test("GET /api/ogloszenia (field mapping)", True, f"✅ All {len(buses)} buses have sold/reserved fields")
                    else:
                        missing_fields = [i for i, bus in enumerate(buses) if 'sold' not in bus or 'reserved' not in bus]
                        self.log_test("GET /api/ogloszenia (field mapping)", False, f"Buses missing sold/reserved fields at indices: {missing_fields}")
                else:
                    self.log_test("GET /api/ogloszenia (field mapping)", False, "No buses returned")
            else:
                self.log_test("GET /api/ogloszenia (field mapping)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/ogloszenia (field mapping)", False, f"Exception: {str(e)}")
        
        # Test 7: Test mutual exclusivity if toggle-reserved works
        # This will only run if toggle-reserved is working
        print("\n   🔄 Testing mutual exclusivity (if toggle-reserved works)...")
        try:
            # First set sold to true
            sold_response = self.session.post(f"{BASE_URL}/ogloszenia/{test_bus_id}/toggle-sold")
            if sold_response.status_code == 200:
                # Then try to set reserved to true (should disable sold)
                reserved_response = self.session.post(f"{BASE_URL}/ogloszenia/{test_bus_id}/toggle-reserved")
                if reserved_response.status_code == 200:
                    result = reserved_response.json()
                    if result.get('reserved') and not result.get('sold'):
                        self.log_test("Mutual exclusivity (sold→reserved)", True, "✅ Setting reserved=True correctly disabled sold")
                    else:
                        self.log_test("Mutual exclusivity (sold→reserved)", False, f"Expected reserved=True, sold=False, got: {result}")
                else:
                    self.log_test("Mutual exclusivity (sold→reserved)", False, "Cannot test - toggle-reserved endpoint not working")
            else:
                self.log_test("Mutual exclusivity (sold→reserved)", False, "Cannot test - toggle-sold endpoint not working")
        except Exception as e:
            self.log_test("Mutual exclusivity (sold→reserved)", False, f"Exception: {str(e)}")

    def test_image_upload(self):
        """Test image upload endpoint"""
        print("\n📷 Testing Image Upload...")
        
        if not self.admin_authenticated:
            self.log_test("Image Upload", False, "Admin authentication required")
            return
        
        # Create a simple test image file in memory
        try:
            # Create a minimal test file
            test_image_content = b"fake_image_content_for_testing"
            files = {'file': ('test_bus_image.jpg', test_image_content, 'image/jpeg')}
            
            response = self.session.post(f"{BASE_URL}/upload", files=files)
            if response.status_code == 200:
                upload_result = response.json()
                self.log_test("POST /api/upload (image upload)", True, f"Upload successful: {upload_result.get('storage', 'unknown')} storage")
            else:
                self.log_test("POST /api/upload (image upload)", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("POST /api/upload (image upload)", False, f"Exception: {str(e)}")
    
    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        if not self.admin_authenticated:
            return
        
        # Delete created bus
        if self.created_bus_id:
            try:
                response = self.session.delete(f"{BASE_URL}/ogloszenia/{self.created_bus_id}")
                if response.status_code == 200:
                    self.log_test("DELETE /api/ogloszenia/{bus_id} (cleanup)", True, "Test bus deleted")
                else:
                    self.log_test("DELETE /api/ogloszenia/{bus_id} (cleanup)", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("DELETE /api/ogloszenia/{bus_id} (cleanup)", False, f"Exception: {str(e)}")
        
        # Delete created opinion
        if self.created_opinion_id:
            try:
                response = self.session.delete(f"{BASE_URL}/opinie/{self.created_opinion_id}")
                if response.status_code == 200:
                    self.log_test("DELETE /api/opinie/{opinion_id} (cleanup)", True, "Test opinion deleted")
                else:
                    self.log_test("DELETE /api/opinie/{opinion_id} (cleanup)", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("DELETE /api/opinie/{opinion_id} (cleanup)", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting FHU Franko Bus Dealership API Tests")
        print(f"🔗 Base URL: {BASE_URL}")
        print("=" * 60)
        
        # Test authentication first
        auth_success = self.test_admin_authentication()
        
        # Test public endpoints (should work without auth)
        self.test_public_endpoints()
        
        # Test admin endpoints (require auth)
        if auth_success:
            self.test_admin_bus_endpoints()
            self.test_rezerwacja_toggle_endpoints()
            self.test_admin_opinion_endpoints()
            self.test_image_upload()
            self.cleanup_test_data()
        else:
            print("⚠️  Skipping admin tests due to authentication failure")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        failed_tests = [result for result in self.test_results if not result['success']]
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if failed_tests:
            print("\n🔍 FAILED TESTS:")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['details']}")
        
        print("\n" + "=" * 60)
        
        # Return exit code
        return 0 if passed == total else 1

def main():
    """Main test runner"""
    tester = BusAPITester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()