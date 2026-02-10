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

class AfroMarketAPITester:
    def __init__(self, base_url: str = "https://afro-market.co.uk"):
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
        self.session_id = None

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

    def test_delivery_api_calculate(self):
        """Test POST /api/delivery/calculate with different postcodes and subtotals"""
        print("\n🚚 Testing Delivery API - Calculate Delivery...")
        
        # Test case 1: London postcode with subtotal under £100
        test_cases = [
            {
                "name": "London postcode (SW1A1AA) - subtotal £50",
                "data": {"postcode": "SW1A1AA", "subtotal": 50.0, "weight_kg": 2.0, "delivery_option": "standard"},
                "expected_free": False
            },
            {
                "name": "Manchester postcode (M1) - subtotal £75", 
                "data": {"postcode": "M1 1AA", "subtotal": 75.0, "weight_kg": 1.5, "delivery_option": "standard"},
                "expected_free": False
            },
            {
                "name": "London postcode (SW1A1AA) - subtotal £120 (FREE delivery)",
                "data": {"postcode": "SW1A1AA", "subtotal": 120.0, "weight_kg": 3.0, "delivery_option": "standard"},
                "expected_free": True
            }
        ]
        
        all_passed = True
        for case in test_cases:
            success, response = self.make_request('POST', 'delivery/calculate', case["data"], auth_required=False)
            
            if success and isinstance(response, dict):
                free_delivery = response.get('free_delivery', False)
                delivery_cost = response.get('delivery_cost', 0)
                zone = response.get('zone', '')
                
                # Check if free delivery expectation matches
                free_delivery_correct = free_delivery == case["expected_free"]
                
                if case["expected_free"]:
                    cost_correct = delivery_cost == 0
                else:
                    cost_correct = delivery_cost > 0
                
                test_passed = free_delivery_correct and cost_correct
                all_passed = all_passed and test_passed
                
                details = f"Zone: {zone}, Cost: £{delivery_cost}, Free: {free_delivery}"
                self.log_test(f"Delivery Calculate - {case['name']}", test_passed, details)
            else:
                all_passed = False
                self.log_test(f"Delivery Calculate - {case['name']}", False, f"API error: {response}")
        
        return all_passed
    
    def test_delivery_api_options(self):
        """Test GET /api/delivery/options with different postcodes and subtotals"""
        print("\n📦 Testing Delivery API - Get Options...")
        
        test_cases = [
            {
                "name": "SW1A1AA with £50 subtotal",
                "params": {"postcode": "SW1A1AA", "subtotal": 50, "weight_kg": 1.0}
            },
            {
                "name": "SW1A1AA with £120 subtotal (FREE delivery)",
                "params": {"postcode": "SW1A1AA", "subtotal": 120, "weight_kg": 1.0}
            },
            {
                "name": "M1 1AA (Manchester) with £75 subtotal",
                "params": {"postcode": "M1 1AA", "subtotal": 75, "weight_kg": 2.0}
            }
        ]
        
        all_passed = True
        for case in test_cases:
            params = case["params"]
            endpoint = f"delivery/options?postcode={params['postcode']}&subtotal={params['subtotal']}&weight_kg={params['weight_kg']}"
            
            success, response = self.make_request('GET', endpoint, auth_required=False)
            
            if success and isinstance(response, dict):
                options = response.get('options', [])
                qualifies_for_free = response.get('qualifies_for_free', False)
                zone = response.get('zone', '')
                
                # Check if we have delivery options
                has_options = len(options) >= 1
                
                # For £120+ orders, should qualify for free delivery
                if params['subtotal'] >= 100:
                    free_delivery_correct = qualifies_for_free
                else:
                    free_delivery_correct = not qualifies_for_free
                
                test_passed = has_options and free_delivery_correct
                all_passed = all_passed and test_passed
                
                details = f"Zone: {zone}, Options: {len(options)}, Free qualifying: {qualifies_for_free}"
                self.log_test(f"Delivery Options - {case['name']}", test_passed, details)
            else:
                all_passed = False
                self.log_test(f"Delivery Options - {case['name']}", False, f"API error: {response}")
        
        return all_passed
    
    def test_delivery_api_zones(self):
        """Test GET /api/delivery/zones"""
        print("\n🗺️ Testing Delivery API - Get Zones...")
        
        success, response = self.make_request('GET', 'delivery/zones', auth_required=False)
        
        if success and isinstance(response, dict):
            zones = response.get('zones', {})
            free_threshold = response.get('free_delivery_threshold', 0)
            
            # Expected zones
            expected_zones = ['local', 'near', 'mid', 'far', 'remote']
            has_all_zones = all(zone in zones for zone in expected_zones)
            
            # Check if free delivery threshold is £100
            correct_threshold = free_threshold == 100.0
            
            test_passed = has_all_zones and correct_threshold
            details = f"Zones: {list(zones.keys())}, Free threshold: £{free_threshold}"
            
            self.log_test("Delivery Zones - All Zones Present", has_all_zones, f"Zones: {list(zones.keys())}")
            self.log_test("Delivery Zones - Free Threshold £100", correct_threshold, f"Threshold: £{free_threshold}")
            
            return test_passed
        else:
            self.log_test("Delivery Zones - Get Zones", False, f"API error: {response}")
            return False
    
    def test_chatbot_api_welcome(self):
        """Test GET /api/chatbot/welcome"""
        print("\n🤖 Testing Chatbot API - Welcome...")
        
        success, response = self.make_request('GET', 'chatbot/welcome', auth_required=False)
        
        if success and isinstance(response, dict):
            success_flag = response.get('success', False)
            welcome_message = response.get('welcome_message', '')
            quick_replies = response.get('quick_replies', [])
            session_id = response.get('session_id', '')
            bot_name = response.get('bot_name', '')
            
            # Check all required fields
            has_welcome = len(welcome_message) > 0
            has_session = len(session_id) > 0
            has_replies = len(quick_replies) >= 3  # Should have at least a few quick replies
            correct_bot_name = bot_name == 'AfroBot'
            
            test_passed = success_flag and has_welcome and has_session and has_replies and correct_bot_name
            
            details = f"Session: {session_id[:8]}..., Replies: {len(quick_replies)}, Bot: {bot_name}"
            self.log_test("Chatbot Welcome - Complete Response", test_passed, details)
            
            # Store session_id for next test
            self.session_id = session_id
            return test_passed
        else:
            self.log_test("Chatbot Welcome - Complete Response", False, f"API error: {response}")
            return False
    
    def test_chatbot_api_message(self):
        """Test POST /api/chatbot/message with test questions"""
        print("\n💬 Testing Chatbot API - Send Message...")
        
        test_cases = [
            {
                "message": "What products do you sell?",
                "expected_keywords": ["african", "products", "groceries"]
            },
            {
                "message": "How much is delivery?",
                "expected_keywords": ["delivery", "£100", "free"]
            }
        ]
        
        all_passed = True
        session_id = getattr(self, 'session_id', None)
        
        for i, case in enumerate(test_cases):
            test_data = {"message": case["message"]}
            if session_id:
                test_data["session_id"] = session_id
            
            success, response = self.make_request('POST', 'chatbot/message', test_data, auth_required=False)
            
            if success and isinstance(response, dict):
                success_flag = response.get('success', False)
                ai_response = response.get('response', '')
                returned_session_id = response.get('session_id', '')
                timestamp = response.get('timestamp', '')
                
                # Check if response is meaningful (length and contains relevant keywords)
                response_meaningful = len(ai_response) > 50
                
                # Update session_id for continuity
                if returned_session_id:
                    session_id = returned_session_id
                
                test_passed = success_flag and response_meaningful and len(timestamp) > 0
                all_passed = all_passed and test_passed
                
                details = f"Response length: {len(ai_response)}, Session: {returned_session_id[:8] if returned_session_id else 'None'}..."
                self.log_test(f"Chatbot Message - '{case['message'][:20]}...'", test_passed, details)
            else:
                all_passed = False
                self.log_test(f"Chatbot Message - '{case['message'][:20]}...'", False, f"API error: {response}")
        
        return all_passed
    
    def test_chatbot_api_quick_replies(self):
        """Test GET /api/chatbot/quick-replies"""
        print("\n⚡ Testing Chatbot API - Quick Replies...")
        
        success, response = self.make_request('GET', 'chatbot/quick-replies', auth_required=False)
        
        if success and isinstance(response, dict):
            success_flag = response.get('success', False)
            quick_replies = response.get('quick_replies', [])
            
            # Check if we have quick replies with proper structure
            has_replies = len(quick_replies) >= 3
            proper_structure = True
            
            if quick_replies:
                # Check if first reply has required fields
                first_reply = quick_replies[0]
                proper_structure = 'id' in first_reply and 'text' in first_reply
            
            test_passed = success_flag and has_replies and proper_structure
            details = f"Replies: {len(quick_replies)}, Structure: {'✓' if proper_structure else '✗'}"
            
            self.log_test("Chatbot Quick Replies - Response Structure", test_passed, details)
            return test_passed
        else:
            self.log_test("Chatbot Quick Replies - Response Structure", False, f"API error: {response}")
            return False
    
    def test_auth_owner_login(self):
        """Test owner login with sotubodammy@gmail.com"""
        print("\n👑 Testing Authentication - Owner Login...")
        
        success, response = self.make_request('POST', 'auth/login', {
            "email": "sotubodammy@gmail.com",
            "password": "NewPassword123!"
        }, auth_required=False)
        
        if success and response.get('success') and response.get('token'):
            self.token = response['token']
            self.user_id = response['user']['id']
            user_email = response['user']['email']
            is_admin = response['user'].get('is_admin', False)
            
            # Store owner token for potential future use
            self.owner_token = self.token
            
            self.log_test("Owner Login - Authentication Success", True, f"Owner: {user_email}, Admin: {is_admin}")
            return True
        else:
            self.log_test("Owner Login - Authentication Success", False, f"Login failed: {response}")
            return False
    
    def test_auth_regular_user_login(self):
        """Test regular user login"""
        print("\n👤 Testing Authentication - Regular User Login...")
        
        success, response = self.make_request('POST', 'auth/login', {
            "email": "test@test.com",
            "password": "Test123!"
        }, auth_required=False)
        
        if success and response.get('success') and response.get('token'):
            token = response['token']
            user_email = response['user']['email']
            
            self.log_test("Regular User Login - Authentication Success", True, f"User: {user_email}")
            return True
        else:
            # Try to create the user first if login fails
            reg_success, reg_response = self.make_request('POST', 'auth/register', {
                "name": "Test User",
                "email": "test@test.com", 
                "password": "Test123!"
            }, auth_required=False)
            
            if reg_success:
                # Now try login again
                success, response = self.make_request('POST', 'auth/login', {
                    "email": "test@test.com",
                    "password": "Test123!"
                }, auth_required=False)
                
                if success and response.get('success'):
                    self.log_test("Regular User Login - After Registration", True, f"User: {response['user']['email']}")
                    return True
            
            self.log_test("Regular User Login - Authentication Success", False, f"Login failed: {response}")
            return False
    
    def test_auth_register_new_user(self):
        """Test new user registration"""
        print("\n📝 Testing Authentication - New User Registration...")
        
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"newuser_{timestamp}@test.com"
        
        success, response = self.make_request('POST', 'auth/register', {
            "name": "New Test User",
            "email": test_email,
            "password": "NewTest123!"
        }, auth_required=False)
        
        if success and response.get('success') and response.get('token'):
            user_email = response['user']['email']
            token_length = len(response['token'])
            
            self.log_test("New User Registration - Success", True, f"User: {user_email}, Token length: {token_length}")
            return True
        else:
            self.log_test("New User Registration - Success", False, f"Registration failed: {response}")
            return False
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

    def run_new_features_tests(self):
        """Run comprehensive test suite for newly implemented features"""
        print("🧪 Starting AfroMarket UK Backend Tests - New Features Testing")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Test the health endpoint first to verify API is running
        print("\n🏥 Testing API Health...")
        success, response = self.make_request('GET', 'health', auth_required=False)
        if success and response.get('status') == 'ok':
            self.log_test("API Health Check", True, f"Status: {response.get('status')}, Message: {response.get('message', '')}")
        else:
            self.log_test("API Health Check", False, f"Health check failed: {response}")
        
        # 1. DELIVERY API TESTS
        print("\n" + "="*50)
        print("🚚 DELIVERY API TESTS")
        print("="*50)
        
        delivery_calculate_success = self.test_delivery_api_calculate()
        delivery_options_success = self.test_delivery_api_options()
        delivery_zones_success = self.test_delivery_api_zones()
        
        # 2. CHATBOT API TESTS
        print("\n" + "="*50)
        print("🤖 CHATBOT API TESTS")
        print("="*50)
        
        chatbot_welcome_success = self.test_chatbot_api_welcome()
        chatbot_message_success = self.test_chatbot_api_message()
        chatbot_replies_success = self.test_chatbot_api_quick_replies()
        
        # 3. AUTHENTICATION TESTS
        print("\n" + "="*50)
        print("🔐 AUTHENTICATION TESTS")
        print("="*50)
        
        owner_login_success = self.test_auth_owner_login()
        regular_user_login_success = self.test_auth_regular_user_login()
        user_registration_success = self.test_auth_register_new_user()
        
        # Print summary
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for failure in self.failed_tests:
                print(f"  - {failure['test']}: {failure['error']}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"\n✨ Success Rate: {success_rate:.1f}%")
        
        # Summary of key features
        print(f"\n📈 Feature Status:")
        print(f"  🚚 Delivery API:")
        print(f"    - Calculate: {'✅' if delivery_calculate_success else '❌'}")
        print(f"    - Options: {'✅' if delivery_options_success else '❌'}")
        print(f"    - Zones: {'✅' if delivery_zones_success else '❌'}")
        print(f"  🤖 Chatbot API:")
        print(f"    - Welcome: {'✅' if chatbot_welcome_success else '❌'}")
        print(f"    - Messages: {'✅' if chatbot_message_success else '❌'}")
        print(f"    - Quick Replies: {'✅' if chatbot_replies_success else '❌'}")
        print(f"  🔐 Authentication:")
        print(f"    - Owner Login: {'✅' if owner_login_success else '❌'}")
        print(f"    - User Login: {'✅' if regular_user_login_success else '❌'}")
        print(f"    - Registration: {'✅' if user_registration_success else '❌'}")
        
        return success_rate >= 70

def main():
    """Main test execution"""
    tester = AfroMarketAPITester()
    
    try:
        success = tester.run_new_features_tests()
        
        # Save detailed results
        with open('/app/backend_test_results.json', 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "test_type": "new_features_testing",
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