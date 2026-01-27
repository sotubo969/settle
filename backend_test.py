#!/usr/bin/env python3
"""
AfroMarket UK Backend API Testing - Vendor Registration & Firebase Auth
Tests vendor registration email notifications and Firebase authentication setup
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class AfroMarketAPITester:
    def __init__(self, base_url: str = "https://github-code-pull.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.test_results = {}

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
            self.failed_tests.append({"test": name, "error": details})
        
        self.test_results[name] = {
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    expected_status: int = 200, auth_required: bool = True) -> tuple:
        """Make API request and return (success, response_data)"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return False, f"Unsupported method: {method}"

            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = {"status_code": response.status_code, "text": response.text}
            
            return success, response_data

        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {str(e)}"

    def test_firebase_status(self):
        """Test Firebase configuration status"""
        print("\n🔥 Testing Firebase Status...")
        
        success, response = self.make_request('GET', 'auth/firebase/status', auth_required=False)
        
        if success and response.get('configured') == True:
            self.log_test("Firebase Status - Configured", True, "Firebase is properly configured")
        else:
            self.log_test("Firebase Status - Configured", False, f"Firebase not configured: {response}")
        
        return success

    def test_authentication(self):
        """Test user authentication (email/password)"""
        print("\n🔐 Testing Email/Password Authentication...")
        
        # Test registration
        test_email = f"test_{datetime.now().strftime('%H%M%S')}@example.com"
        success, response = self.make_request('POST', 'auth/register', {
            "name": "Test User",
            "email": test_email,
            "password": "Test123!"
        }, auth_required=False)
        
        if success and response.get('token'):
            self.token = response['token']
            self.user_id = response['user']['id']
            self.log_test("Email/Password Registration", True)
        else:
            self.log_test("Email/Password Registration", False, str(response))
            return False

        # Test login
        success, response = self.make_request('POST', 'auth/login', {
            "email": test_email,
            "password": "Test123!"
        }, auth_required=False)
        
        if success and response.get('token'):
            self.log_test("Email/Password Login", True)
        else:
            self.log_test("Email/Password Login", False, str(response))
        
        return True

    def test_vendor_registration_public(self):
        """Test public vendor registration endpoint with email notification"""
        print("\n🏪 Testing Public Vendor Registration...")
        
        # Test public vendor registration (no auth required)
        timestamp = datetime.now().strftime('%H%M%S')
        vendor_data = {
            "businessName": f"Test African Store {timestamp}",
            "description": "A test store selling authentic African products and groceries",
            "email": f"vendor_{timestamp}@teststore.com",
            "phone": "+44 20 1234 5678",
            "address": "123 Test Street",
            "city": "London",
            "postcode": "SW1A 1AA",
            "ownerName": "Test Owner"
        }
        
        success, response = self.make_request('POST', 'vendors/register/public', vendor_data, auth_required=False)
        
        if success and response.get('success'):
            email_sent = response.get('emailSent', False)
            vendor_id = response.get('vendor', {}).get('id')
            
            self.log_test("Public Vendor Registration - Success", True, f"Vendor ID: {vendor_id}")
            self.log_test("Public Vendor Registration - Email Sent", email_sent, 
                         f"Email sent status: {email_sent}")
            
            # Check if response includes proper message
            message = response.get('message', '')
            expected_message_parts = ['submitted successfully', 'review', 'contact']
            message_ok = any(part in message.lower() for part in expected_message_parts)
            self.log_test("Public Vendor Registration - Message", message_ok, f"Message: {message}")
            
            return vendor_id
        else:
            self.log_test("Public Vendor Registration - Success", False, str(response))
            return None

    def test_vendor_registration_authenticated(self):
        """Test authenticated vendor registration endpoint"""
        print("\n🏪 Testing Authenticated Vendor Registration...")
        
        if not self.token:
            self.log_test("Authenticated Vendor Registration", False, "No auth token available")
            return None
        
        # Test authenticated vendor registration
        timestamp = datetime.now().strftime('%H%M%S')
        vendor_data = {
            "businessName": f"Test Authenticated Store {timestamp}",
            "description": "A test store for authenticated user registration",
            "email": f"auth_vendor_{timestamp}@teststore.com",
            "phone": "+44 20 9876 5432",
            "address": "456 Auth Street",
            "city": "Manchester",
            "postcode": "M1 1AA"
        }
        
        success, response = self.make_request('POST', 'vendors/register', vendor_data, auth_required=True)
        
        if success and response.get('success'):
            vendor_id = response.get('vendor', {}).get('id')
            self.log_test("Authenticated Vendor Registration", True, f"Vendor ID: {vendor_id}")
            return vendor_id
        else:
            self.log_test("Authenticated Vendor Registration", False, str(response))
            return None

    def test_basic_endpoints(self):
        """Test basic API endpoints are working"""
        print("\n🌐 Testing Basic API Endpoints...")
        
        # Test products endpoint
        success, response = self.make_request('GET', 'products', auth_required=False)
        if success and isinstance(response, list):
            self.log_test("Products API", True, f"Found {len(response)} products")
        else:
            self.log_test("Products API", False, str(response))
        
        # Test vendors endpoint
        success, response = self.make_request('GET', 'vendors', auth_required=False)
        if success and isinstance(response, list):
            self.log_test("Vendors API", True, f"Found {len(response)} vendors")
        else:
            self.log_test("Vendors API", False, str(response))

    def run_all_tests(self):
        """Run comprehensive test suite for vendor registration and Firebase"""
        print("🧪 Starting AfroMarket UK Backend Tests - Vendor Registration & Firebase")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Test Firebase configuration
        self.test_firebase_status()
        
        # Test basic endpoints
        self.test_basic_endpoints()
        
        # Test authentication
        auth_success = self.test_authentication()
        
        # Test vendor registration (both public and authenticated)
        self.test_vendor_registration_public()
        
        if auth_success:
            self.test_vendor_registration_authenticated()
        
        # Print summary
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for failure in self.failed_tests:
                print(f"  - {failure['test']}: {failure['error']}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"\n✨ Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 70

def main():
    """Main test execution"""
    tester = AfroMarketAPITester()
    
    try:
        success = tester.run_all_tests()
        
        # Save detailed results
        with open('/app/backend_test_results.json', 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_tests": tester.tests_run,
                "passed_tests": tester.tests_passed,
                "failed_tests": tester.failed_tests,
                "success_rate": (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0,
                "detailed_results": tester.test_results
            }, f, indent=2)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"💥 Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())