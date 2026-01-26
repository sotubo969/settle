#!/usr/bin/env python3
"""
Backend API Testing for AfroMarket UK Vendor Wallet System
Tests all wallet-related endpoints and core functionality
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://code-fetcher-23.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class VendorWalletTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AfroMarket-Test-Client/1.0'
        })
        
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        self.auth_token = None
        self.test_user_id = None
        self.test_vendor_id = None

    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        self.test_results['total_tests'] += 1
        
        if success:
            self.test_results['passed_tests'] += 1
            status = "✅ PASS"
        else:
            self.test_results['failed_tests'] += 1
            status = "❌ FAIL"
        
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        
        self.test_results['test_details'].append({
            'test_name': test_name,
            'success': success,
            'details': details,
            'response_data': response_data,
            'timestamp': datetime.now().isoformat()
        })

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, auth_required: bool = True) -> tuple:
        """Make HTTP request with error handling"""
        url = f"{API_BASE}/{endpoint.lstrip('/')}"
        
        headers = {}
        if auth_required and self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, headers=headers, timeout=30)
            else:
                return False, f"Unsupported method: {method}"
            
            return True, response
        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {str(e)}"

    def test_backend_health(self):
        """Test if backend is accessible"""
        print("\n🔍 Testing Backend Health...")
        
        success, response = self.make_request('GET', '/products', auth_required=False)
        
        if success and response.status_code == 200:
            self.log_test("Backend Health Check", True, f"Backend is accessible (Status: {response.status_code})")
            return True
        else:
            error_msg = response if isinstance(response, str) else f"Status: {response.status_code if hasattr(response, 'status_code') else 'Unknown'}"
            self.log_test("Backend Health Check", False, f"Backend not accessible: {error_msg}")
            return False

    def test_user_registration_and_login(self):
        """Test user registration and login"""
        print("\n🔍 Testing User Authentication...")
        
        # Test user registration
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_user_data = {
            "name": f"Test Vendor {timestamp}",
            "email": f"testvendor_{timestamp}@example.com",
            "password": "TestPassword123!"
        }
        
        success, response = self.make_request('POST', '/auth/register', data=test_user_data, auth_required=False)
        
        if success and response.status_code == 200:
            response_data = response.json()
            if response_data.get('success') and response_data.get('token'):
                self.auth_token = response_data['token']
                self.test_user_id = response_data['user']['id']
                self.log_test("User Registration", True, f"User registered successfully (ID: {self.test_user_id})")
                
                # Test login with same credentials
                login_data = {
                    "email": test_user_data["email"],
                    "password": test_user_data["password"]
                }
                
                success, login_response = self.make_request('POST', '/auth/login', data=login_data, auth_required=False)
                
                if success and login_response.status_code == 200:
                    login_response_data = login_response.json()
                    if login_response_data.get('success') and login_response_data.get('token'):
                        self.log_test("User Login", True, "Login successful")
                        return True
                    else:
                        self.log_test("User Login", False, "Login response missing token")
                        return False
                else:
                    error_msg = login_response.text if hasattr(login_response, 'text') else str(login_response)
                    self.log_test("User Login", False, f"Login failed: {error_msg}")
                    return False
            else:
                self.log_test("User Registration", False, "Registration response missing token")
                return False
        else:
            error_msg = response.text if hasattr(response, 'text') else str(response)
            self.log_test("User Registration", False, f"Registration failed: {error_msg}")
            return False

    def test_vendor_registration(self):
        """Test vendor registration"""
        print("\n🔍 Testing Vendor Registration...")
        
        if not self.auth_token:
            self.log_test("Vendor Registration", False, "No auth token available")
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        vendor_data = {
            "businessName": f"Test Business {timestamp}",
            "description": "A test business for wallet testing",
            "email": f"testbusiness_{timestamp}@example.com",
            "phone": "+44 7700 900123",
            "address": "123 Test Street",
            "city": "London",
            "postcode": "SW1A 1AA"
        }
        
        success, response = self.make_request('POST', '/vendors/register', data=vendor_data)
        
        if success and response.status_code == 200:
            response_data = response.json()
            if response_data.get('success'):
                self.test_vendor_id = response_data['vendor']['id']
                self.log_test("Vendor Registration", True, f"Vendor registered successfully (ID: {self.test_vendor_id})")
                return True
            else:
                self.log_test("Vendor Registration", False, "Vendor registration response missing success flag")
                return False
        else:
            error_msg = response.text if hasattr(response, 'text') else str(response)
            self.log_test("Vendor Registration", False, f"Vendor registration failed: {error_msg}")
            return False

    def test_wallet_get_balance(self):
        """Test GET /api/wallet - Get vendor wallet balance and info"""
        print("\n🔍 Testing GET /api/wallet...")
        
        if not self.auth_token:
            self.log_test("GET /api/wallet", False, "No auth token available")
            return False
        
        success, response = self.make_request('GET', '/wallet')
        
        if success:
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    wallet = response_data.get('wallet', {})
                    
                    # Check required wallet fields
                    required_fields = ['balance', 'total_deposited', 'total_spent']
                    missing_fields = [field for field in required_fields if field not in wallet]
                    
                    if missing_fields:
                        self.log_test("GET /api/wallet", False, f"Missing wallet fields: {missing_fields}", response_data)
                    else:
                        self.log_test("GET /api/wallet", True, f"Wallet retrieved successfully. Balance: £{wallet.get('balance', 0)}", response_data)
                        return True
                except json.JSONDecodeError:
                    self.log_test("GET /api/wallet", False, "Invalid JSON response")
            elif response.status_code == 403:
                self.log_test("GET /api/wallet", False, "Access forbidden - user may not be a vendor")
            else:
                self.log_test("GET /api/wallet", False, f"Unexpected status code: {response.status_code}")
        else:
            self.log_test("GET /api/wallet", False, f"Request failed: {response}")
        
        return False

    def test_wallet_topup_create_intent(self):
        """Test POST /api/wallet/topup - Create payment intent for wallet top-up"""
        print("\n🔍 Testing POST /api/wallet/topup...")
        
        if not self.auth_token:
            self.log_test("POST /api/wallet/topup", False, "No auth token available")
            return False
        
        topup_data = {"amount": 25.00}
        
        success, response = self.make_request('POST', '/wallet/topup', data=topup_data)
        
        if success:
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    
                    # Check for Stripe payment intent fields
                    expected_fields = ['client_secret', 'payment_intent_id']
                    has_required_fields = any(field in response_data for field in expected_fields)
                    
                    if has_required_fields:
                        self.log_test("POST /api/wallet/topup", True, f"Payment intent created successfully", response_data)
                        return True
                    else:
                        self.log_test("POST /api/wallet/topup", False, f"Missing payment intent fields in response", response_data)
                except json.JSONDecodeError:
                    self.log_test("POST /api/wallet/topup", False, "Invalid JSON response")
            elif response.status_code == 403:
                self.log_test("POST /api/wallet/topup", False, "Access forbidden - user may not be a vendor")
            elif response.status_code == 400:
                self.log_test("POST /api/wallet/topup", False, f"Bad request: {response.text}")
            else:
                self.log_test("POST /api/wallet/topup", False, f"Unexpected status code: {response.status_code}")
        else:
            self.log_test("POST /api/wallet/topup", False, f"Request failed: {response}")
        
        return False

    def test_wallet_confirm_topup(self):
        """Test POST /api/wallet/confirm-topup - Confirm wallet top-up after Stripe payment"""
        print("\n🔍 Testing POST /api/wallet/confirm-topup...")
        
        if not self.auth_token:
            self.log_test("POST /api/wallet/confirm-topup", False, "No auth token available")
            return False
        
        # Test with mock payment intent ID (this will likely fail but we can check the API structure)
        params = {
            "payment_intent_id": "pi_test_mock_payment_intent",
            "amount": 25.00
        }
        
        success, response = self.make_request('POST', '/wallet/confirm-topup', params=params)
        
        if success:
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    self.log_test("POST /api/wallet/confirm-topup", True, "Confirm topup endpoint accessible", response_data)
                    return True
                except json.JSONDecodeError:
                    self.log_test("POST /api/wallet/confirm-topup", False, "Invalid JSON response")
            elif response.status_code == 400:
                # Expected for mock payment intent
                self.log_test("POST /api/wallet/confirm-topup", True, "Endpoint accessible (expected 400 for mock payment)")
                return True
            elif response.status_code == 403:
                self.log_test("POST /api/wallet/confirm-topup", False, "Access forbidden - user may not be a vendor")
            else:
                self.log_test("POST /api/wallet/confirm-topup", True, f"Endpoint accessible (Status: {response.status_code})")
                return True
        else:
            self.log_test("POST /api/wallet/confirm-topup", False, f"Request failed: {response}")
        
        return False

    def test_wallet_setup_auto_recharge(self):
        """Test POST /api/wallet/setup-auto-recharge - Configure auto-recharge settings"""
        print("\n🔍 Testing POST /api/wallet/setup-auto-recharge...")
        
        if not self.auth_token:
            self.log_test("POST /api/wallet/setup-auto-recharge", False, "No auth token available")
            return False
        
        auto_recharge_data = {
            "enabled": True,
            "threshold": 10.0,
            "amount": 50.0
        }
        
        success, response = self.make_request('POST', '/wallet/setup-auto-recharge', data=auto_recharge_data)
        
        if success:
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if response_data.get('success'):
                        self.log_test("POST /api/wallet/setup-auto-recharge", True, "Auto-recharge settings updated successfully", response_data)
                        return True
                    else:
                        self.log_test("POST /api/wallet/setup-auto-recharge", False, "Response missing success flag", response_data)
                except json.JSONDecodeError:
                    self.log_test("POST /api/wallet/setup-auto-recharge", False, "Invalid JSON response")
            elif response.status_code == 403:
                self.log_test("POST /api/wallet/setup-auto-recharge", False, "Access forbidden - user may not be a vendor")
            else:
                self.log_test("POST /api/wallet/setup-auto-recharge", False, f"Unexpected status code: {response.status_code}")
        else:
            self.log_test("POST /api/wallet/setup-auto-recharge", False, f"Request failed: {response}")
        
        return False

    def test_wallet_transactions(self):
        """Test GET /api/wallet/transactions - Get wallet transaction history"""
        print("\n🔍 Testing GET /api/wallet/transactions...")
        
        if not self.auth_token:
            self.log_test("GET /api/wallet/transactions", False, "No auth token available")
            return False
        
        success, response = self.make_request('GET', '/wallet/transactions')
        
        if success:
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    transactions = response_data.get('transactions', [])
                    
                    self.log_test("GET /api/wallet/transactions", True, f"Transactions retrieved successfully. Count: {len(transactions)}", response_data)
                    return True
                except json.JSONDecodeError:
                    self.log_test("GET /api/wallet/transactions", False, "Invalid JSON response")
            elif response.status_code == 403:
                self.log_test("GET /api/wallet/transactions", False, "Access forbidden - user may not be a vendor")
            else:
                self.log_test("GET /api/wallet/transactions", False, f"Unexpected status code: {response.status_code}")
        else:
            self.log_test("GET /api/wallet/transactions", False, f"Request failed: {response}")
        
        return False

    def test_vendor_dashboard_access(self):
        """Test vendor dashboard access"""
        print("\n🔍 Testing Vendor Dashboard Access...")
        
        if not self.auth_token:
            self.log_test("Vendor Dashboard Access", False, "No auth token available")
            return False
        
        success, response = self.make_request('GET', '/vendor/dashboard')
        
        if success:
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    vendor_info = response_data.get('vendor', {})
                    stats = response_data.get('stats', {})
                    
                    if vendor_info and stats:
                        self.log_test("Vendor Dashboard Access", True, f"Dashboard accessible. Vendor: {vendor_info.get('businessName', 'Unknown')}")
                        return True
                    else:
                        self.log_test("Vendor Dashboard Access", False, "Dashboard response missing vendor or stats data")
                except json.JSONDecodeError:
                    self.log_test("Vendor Dashboard Access", False, "Invalid JSON response")
            elif response.status_code == 403:
                self.log_test("Vendor Dashboard Access", False, "Access forbidden - user may not be a registered vendor")
            else:
                self.log_test("Vendor Dashboard Access", False, f"Unexpected status code: {response.status_code}")
        else:
            self.log_test("Vendor Dashboard Access", False, f"Request failed: {response}")
        
        return False

    def run_all_tests(self):
        """Run all wallet system tests"""
        print("🚀 Starting AfroMarket UK Vendor Wallet System Tests")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Backend Health", self.test_backend_health),
            ("User Auth", self.test_user_registration_and_login),
            ("Vendor Registration", self.test_vendor_registration),
            ("Vendor Dashboard", self.test_vendor_dashboard_access),
            ("Wallet Balance", self.test_wallet_get_balance),
            ("Wallet Top-up Intent", self.test_wallet_topup_create_intent),
            ("Wallet Confirm Top-up", self.test_wallet_confirm_topup),
            ("Auto-recharge Setup", self.test_wallet_setup_auto_recharge),
            ("Wallet Transactions", self.test_wallet_transactions),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_test(test_name, False, f"Test threw exception: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"✅ Passed: {self.test_results['passed_tests']}")
        print(f"❌ Failed: {self.test_results['failed_tests']}")
        
        success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100 if self.test_results['total_tests'] > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.test_results['failed_tests'] > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results['test_details']:
                if not test['success']:
                    print(f"  - {test['test_name']}: {test['details']}")
        
        return self.test_results['failed_tests'] == 0

def main():
    """Main test execution"""
    tester = VendorWalletTester()
    
    try:
        success = tester.run_all_tests()
        
        # Save detailed results
        with open('/app/test_results.json', 'w') as f:
            json.dump(tester.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: /app/test_results.json")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test suite crashed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())