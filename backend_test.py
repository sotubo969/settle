#!/usr/bin/env python3
"""
AfroMarket UK Backend API Testing - New Features Testing
Tests newly implemented Delivery API, Chatbot API, and Authentication features
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class AfroMarketFirestoreTester:
    def __init__(self, base_url: str = "https://github-code-pull.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.vendor_id = None
        self.vendor_email = None
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

    def test_health_endpoint(self):
        """Test health endpoint returns database=firestore"""
        print("\n🏥 Testing Health Endpoint...")
        
        success, response = self.make_request('GET', 'health', auth_required=False)
        
        if success and response.get('status') == 'ok':
            database = response.get('database')
            if database == 'firestore':
                self.log_test("Health Endpoint - Database Firestore", True, f"Database: {database}")
                return True
            else:
                self.log_test("Health Endpoint - Database Firestore", False, f"Expected 'firestore', got '{database}'")
                return False
        else:
            self.log_test("Health Endpoint - Database Firestore", False, f"Health check failed: {response}")
            return False

    def test_products_api(self):
        """Test products API returns products from Firestore"""
        print("\n📦 Testing Products API...")
        
        success, response = self.make_request('GET', 'products', auth_required=False)
        
        if success and isinstance(response, list):
            product_count = len(response)
            if product_count > 0:
                # Check if products have expected structure
                first_product = response[0]
                expected_fields = ['id', 'name', 'price', 'category']
                has_fields = all(field in first_product for field in expected_fields)
                
                self.log_test("Products API - Returns Products", True, f"Found {product_count} products")
                self.log_test("Products API - Product Structure", has_fields, f"Fields: {list(first_product.keys())}")
                return product_count
            else:
                self.log_test("Products API - Returns Products", False, "No products found")
                return 0
        else:
            self.log_test("Products API - Returns Products", False, f"API error: {response}")
            return 0

    def test_vendors_api(self):
        """Test vendors API returns 3 vendors"""
        print("\n🏪 Testing Vendors API...")
        
        success, response = self.make_request('GET', 'vendors', auth_required=False)
        
        if success and isinstance(response, list):
            vendor_count = len(response)
            expected_count = 3
            
            if vendor_count >= expected_count:
                # Check vendor structure
                if vendor_count > 0:
                    first_vendor = response[0]
                    expected_fields = ['id', 'name', 'verified']
                    has_fields = all(field in first_vendor for field in expected_fields)
                    
                    self.log_test("Vendors API - Returns 3+ Vendors", True, f"Found {vendor_count} vendors")
                    self.log_test("Vendors API - Vendor Structure", has_fields, f"Fields: {list(first_vendor.keys())}")
                else:
                    self.log_test("Vendors API - Returns 3+ Vendors", False, "No vendors found")
                    
                return vendor_count
            else:
                self.log_test("Vendors API - Returns 3+ Vendors", False, f"Expected {expected_count}+, got {vendor_count}")
                return vendor_count
        else:
            self.log_test("Vendors API - Returns 3+ Vendors", False, f"API error: {response}")
            return 0

    def test_user_registration(self):
        """Test user registration works with Firestore"""
        print("\n👤 Testing User Registration...")
        
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"test_firestore_{timestamp}@example.com"
        
        success, response = self.make_request('POST', 'auth/register', {
            "name": "Firestore Test User",
            "email": test_email,
            "password": "TestPass123!"
        }, auth_required=False)
        
        if success and response.get('success') and response.get('token'):
            self.token = response['token']
            self.user_id = response['user']['id']
            user_name = response['user']['name']
            
            self.log_test("User Registration - Creates User", True, f"User ID: {self.user_id}")
            self.log_test("User Registration - Returns Token", True, f"Token length: {len(self.token)}")
            self.log_test("User Registration - User Data", user_name == "Firestore Test User", f"Name: {user_name}")
            return True
        else:
            self.log_test("User Registration - Creates User", False, f"Registration failed: {response}")
            return False

    def test_user_login(self):
        """Test user login works and returns JWT token"""
        print("\n🔐 Testing User Login...")
        
        # Try with the provided test credentials first
        success, response = self.make_request('POST', 'auth/login', {
            "email": "test@afromarket.co.uk",
            "password": "TestPass123!"
        }, auth_required=False)
        
        if success and response.get('success') and response.get('token'):
            self.token = response['token']
            self.user_id = response['user']['id']
            
            self.log_test("User Login - Test Credentials", True, f"Logged in as {response['user']['email']}")
            return True
        else:
            # If test credentials don't work, try creating a new user
            timestamp = datetime.now().strftime('%H%M%S')
            test_email = f"login_test_{timestamp}@example.com"
            
            # Register first
            reg_success, reg_response = self.make_request('POST', 'auth/register', {
                "name": "Login Test User",
                "email": test_email,
                "password": "TestPass123!"
            }, auth_required=False)
            
            if reg_success:
                # Now try login
                success, response = self.make_request('POST', 'auth/login', {
                    "email": test_email,
                    "password": "TestPass123!"
                }, auth_required=False)
                
                if success and response.get('success') and response.get('token'):
                    self.token = response['token']
                    self.user_id = response['user']['id']
                    
                    self.log_test("User Login - New User Credentials", True, f"Logged in as {response['user']['email']}")
                    return True
            
            self.log_test("User Login - Authentication", False, f"Login failed: {response}")
            return False

    def test_auth_me_endpoint(self):
        """Test authenticated /auth/me endpoint works"""
        print("\n🔒 Testing /auth/me Endpoint...")
        
        if not self.token:
            self.log_test("Auth Me - No Token", False, "No authentication token available")
            return False
        
        success, response = self.make_request('GET', 'auth/me', auth_required=True)
        
        if success and response.get('success'):
            user_data = response.get('user', {})
            expected_fields = ['id', 'name', 'email']
            has_fields = all(field in user_data for field in expected_fields)
            
            self.log_test("Auth Me - Returns User Data", has_fields, f"User: {user_data.get('email')}")
            self.log_test("Auth Me - User ID Match", user_data.get('id') == self.user_id, f"ID: {user_data.get('id')}")
            return has_fields
        else:
            self.log_test("Auth Me - Returns User Data", False, f"Auth me failed: {response}")
            return False

    def test_vendor_registration_firestore(self):
        """Test vendor registration creates vendor in Firestore and sends email"""
        print("\n🏪 Testing Vendor Registration with Firestore...")
        
        timestamp = datetime.now().strftime('%H%M%S')
        self.vendor_email = f"vendor_firestore_{timestamp}@example.com"
        
        vendor_data = {
            "businessName": f"Firestore Test Store {timestamp}",
            "description": "A test store for Firestore migration testing",
            "email": self.vendor_email,
            "phone": "+44 20 1234 5678",
            "address": "123 Firestore Street",
            "city": "London",
            "postcode": "SW1A 1AA",
            "ownerName": "Firestore Test Owner"
        }
        
        success, response = self.make_request('POST', 'vendors/register/public', vendor_data, auth_required=False)
        
        if success and response.get('success'):
            self.vendor_id = response.get('vendor', {}).get('id')
            email_sent = response.get('emailSent', False)
            message = response.get('message', '')
            
            self.log_test("Vendor Registration - Creates in Firestore", True, f"Vendor ID: {self.vendor_id}")
            self.log_test("Vendor Registration - Email Notification", email_sent, f"Email sent: {email_sent}")
            self.log_test("Vendor Registration - Response Message", 'review' in message.lower(), f"Message: {message}")
            return True
        else:
            self.log_test("Vendor Registration - Creates in Firestore", False, f"Registration failed: {response}")
            return False

    def test_contact_form_submission(self):
        """Test contact form submission works"""
        print("\n📧 Testing Contact Form Submission...")
        
        timestamp = datetime.now().strftime('%H%M%S')
        contact_data = {
            "name": f"Firestore Test Contact {timestamp}",
            "email": f"contact_test_{timestamp}@example.com",
            "subject": "Firestore Migration Test",
            "message": "This is a test message to verify contact form works with Firestore."
        }
        
        success, response = self.make_request('POST', 'contact', contact_data, auth_required=False)
        
        if success and response.get('success'):
            message = response.get('message', '')
            self.log_test("Contact Form - Submission Works", True, f"Response: {message}")
            return True
        else:
            self.log_test("Contact Form - Submission Works", False, f"Contact form failed: {response}")
            return False

    def test_firebase_auth_status(self):
        """Test Firebase auth status returns configured=true"""
        print("\n🔥 Testing Firebase Auth Status...")
        
        success, response = self.make_request('GET', 'auth/firebase/status', auth_required=False)
        
        if success:
            configured = response.get('configured', False)
            message = response.get('message', '')
            
            self.log_test("Firebase Auth - Configured Status", configured, f"Message: {message}")
            return configured
        else:
            self.log_test("Firebase Auth - Configured Status", False, f"Status check failed: {response}")
            return False

    def test_notifications_endpoints(self):
        """Test notifications endpoints work"""
        print("\n🔔 Testing Notifications Endpoints...")
        
        if not self.vendor_email:
            self.log_test("Notifications - No Vendor Email", False, "No vendor email for testing")
            return False
        
        # Test vendor notifications by email (public endpoint)
        success, response = self.make_request('GET', f'vendor/notifications/by-email/{self.vendor_email}', 
                                            auth_required=False)
        
        if success and response.get('success'):
            notifications = response.get('notifications', [])
            unread_count = response.get('unreadCount', 0)
            vendor_status = response.get('vendorStatus')
            
            self.log_test("Notifications - By Email Endpoint", True, 
                         f"Found {len(notifications)} notifications, {unread_count} unread")
            self.log_test("Notifications - Vendor Status", vendor_status is not None, 
                         f"Vendor status: {vendor_status}")
            
            # Test authenticated notifications if we have a token
            if self.token:
                success2, response2 = self.make_request('GET', 'vendor/notifications', auth_required=True)
                if success2 and response2.get('success'):
                    auth_notifications = response2.get('notifications', [])
                    self.log_test("Notifications - Authenticated Endpoint", True, 
                                 f"Found {len(auth_notifications)} notifications via auth")
                else:
                    self.log_test("Notifications - Authenticated Endpoint", False, f"Auth notifications failed: {response2}")
            
            return True
        else:
            self.log_test("Notifications - By Email Endpoint", False, f"Notifications failed: {response}")
            return False

    def run_firestore_migration_tests(self):
        """Run comprehensive test suite for Firestore migration"""
        print("🧪 Starting AfroMarket UK Backend Tests - Firestore Migration")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Core Firestore Migration Tests
        print("\n" + "="*50)
        print("🔥 FIRESTORE MIGRATION TESTS")
        print("="*50)
        
        # 1. Health endpoint returns database=firestore
        self.test_health_endpoint()
        
        # 2. Products API returns products from Firestore
        product_count = self.test_products_api()
        
        # 3. Vendors API returns 3 vendors
        vendor_count = self.test_vendors_api()
        
        # 4. User registration works with Firestore
        registration_success = self.test_user_registration()
        
        # 5. User login works and returns JWT token
        login_success = self.test_user_login()
        
        # 6. Authenticated /auth/me endpoint works
        if self.token:
            self.test_auth_me_endpoint()
        
        # 7. Vendor registration creates vendor in Firestore and sends email
        vendor_registration_success = self.test_vendor_registration_firestore()
        
        # 8. Contact form submission works
        self.test_contact_form_submission()
        
        # 9. Firebase auth status returns configured=true
        self.test_firebase_auth_status()
        
        # 10. Notifications endpoints work
        if vendor_registration_success:
            self.test_notifications_endpoints()
        
        # Print summary
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for failure in self.failed_tests:
                print(f"  - {failure['test']}: {failure['error']}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"\n✨ Success Rate: {success_rate:.1f}%")
        
        # Summary of key metrics
        print(f"\n📈 Key Metrics:")
        print(f"  - Products in Firestore: {product_count}")
        print(f"  - Vendors in Firestore: {vendor_count}")
        print(f"  - User Registration: {'✅' if registration_success else '❌'}")
        print(f"  - User Login: {'✅' if login_success else '❌'}")
        print(f"  - Vendor Registration: {'✅' if vendor_registration_success else '❌'}")
        
        return success_rate >= 70

def main():
    """Main test execution"""
    tester = AfroMarketFirestoreTester()
    
    try:
        success = tester.run_firestore_migration_tests()
        
        # Save detailed results
        with open('/app/backend_test_results.json', 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "test_type": "firestore_migration",
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