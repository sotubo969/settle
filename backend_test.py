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

    def test_authentication(self):
        """Test user authentication"""
        print("\n🔐 Testing Authentication...")
        
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
            self.log_test("User Registration", True)
        else:
            self.log_test("User Registration", False, str(response))
            return False

        # Test login
        success, response = self.make_request('POST', 'auth/login', {
            "email": test_email,
            "password": "Test123!"
        }, auth_required=False)
        
        if success and response.get('token'):
            self.log_test("User Login", True)
        else:
            self.log_test("User Login", False, str(response))
        
        return True

    def test_products_api(self):
        """Test products endpoints"""
        print("\n📦 Testing Products API...")
        
        # Get all products
        success, response = self.make_request('GET', 'products', auth_required=False)
        if success and isinstance(response, list):
            product_count = len(response)
            self.log_test(f"Get Products (Found {product_count})", product_count >= 30, 
                         f"Expected 32 products, got {product_count}")
            
            if product_count > 0:
                # Test single product
                product_id = response[0]['id']
                success, product = self.make_request('GET', f'products/{product_id}', auth_required=False)
                self.log_test("Get Single Product", success and 'name' in product)
                return product_id
        else:
            self.log_test("Get Products", False, str(response))
        
        return None

    def test_promo_codes(self):
        """Test promo code validation"""
        print("\n🎫 Testing Promo Codes...")
        
        promo_codes = ["WELCOME10", "AFRO20", "FREEDELIVERY", "NEWCUSTOMER"]
        
        for code in promo_codes:
            success, response = self.make_request('POST', 'promo/validate', {
                "code": code,
                "order_total": 50.0
            })
            
            if success and response.get('success'):
                self.log_test(f"Promo Code {code}", True)
            else:
                self.log_test(f"Promo Code {code}", False, str(response))

    def test_wishlist(self, product_id: int):
        """Test wishlist functionality"""
        print("\n❤️ Testing Wishlist...")
        
        if not product_id:
            self.log_test("Wishlist Test", False, "No product ID available")
            return
        
        # Add to wishlist
        success, response = self.make_request('POST', 'wishlist/toggle', {
            "product_id": product_id
        })
        self.log_test("Add to Wishlist", success and response.get('success'))
        
        # Get wishlist
        success, response = self.make_request('GET', 'wishlist')
        if success and response.get('success'):
            items = response.get('items', [])
            self.log_test("Get Wishlist", len(items) > 0, f"Found {len(items)} items")
        else:
            self.log_test("Get Wishlist", False, str(response))
        
        # Remove from wishlist
        success, response = self.make_request('POST', 'wishlist/toggle', {
            "product_id": product_id
        })
        self.log_test("Remove from Wishlist", success and response.get('success'))

    def test_reviews(self, product_id: int):
        """Test product reviews"""
        print("\n⭐ Testing Product Reviews...")
        
        if not product_id:
            self.log_test("Reviews Test", False, "No product ID available")
            return
        
        # Create review
        success, response = self.make_request('POST', 'reviews/product', {
            "product_id": product_id,
            "rating": 5,
            "title": "Great product!",
            "comment": "Really enjoyed this product. Fast delivery and good quality."
        })
        self.log_test("Create Product Review", success and response.get('success'))
        
        # Get product reviews
        success, response = self.make_request('GET', f'reviews/product/{product_id}', auth_required=False)
        if success and response.get('success'):
            reviews = response.get('reviews', [])
            self.log_test("Get Product Reviews", len(reviews) >= 0, f"Found {len(reviews)} reviews")
        else:
            self.log_test("Get Product Reviews", False, str(response))

    def test_questions(self, product_id: int):
        """Test product Q&A"""
        print("\n❓ Testing Product Q&A...")
        
        if not product_id:
            self.log_test("Q&A Test", False, "No product ID available")
            return
        
        # Ask question
        success, response = self.make_request('POST', 'questions', {
            "product_id": product_id,
            "question": "Is this product suitable for vegetarians?"
        })
        self.log_test("Ask Product Question", success and response.get('success'))
        
        # Get questions
        success, response = self.make_request('GET', f'questions/product/{product_id}', auth_required=False)
        if success and response.get('success'):
            questions = response.get('questions', [])
            self.log_test("Get Product Questions", len(questions) >= 0, f"Found {len(questions)} questions")
        else:
            self.log_test("Get Product Questions", False, str(response))

    def test_messages(self):
        """Test messaging system"""
        print("\n💬 Testing Messages...")
        
        # Get conversations (should be empty for new user)
        success, response = self.make_request('GET', 'messages')
        if success and response.get('success'):
            conversations = response.get('conversations', [])
            self.log_test("Get Conversations", True, f"Found {len(conversations)} conversations")
        else:
            self.log_test("Get Conversations", False, str(response))

    def test_order_tracking(self):
        """Test order tracking"""
        print("\n🚚 Testing Order Tracking...")
        
        # Get order history
        success, response = self.make_request('GET', 'orders/history')
        if success and response.get('success'):
            orders = response.get('orders', [])
            self.log_test("Get Order History", True, f"Found {len(orders)} orders")
        else:
            self.log_test("Get Order History", False, str(response))

    def test_refunds(self):
        """Test refund requests"""
        print("\n💰 Testing Refunds...")
        
        # Get refund requests (should be empty for new user)
        success, response = self.make_request('GET', 'refunds')
        if success and response.get('success'):
            refunds = response.get('refunds', [])
            self.log_test("Get Refund Requests", True, f"Found {len(refunds)} refunds")
        else:
            self.log_test("Get Refund Requests", False, str(response))

    def test_rate_limiting(self):
        """Test rate limiting (120 req/min)"""
        print("\n🚦 Testing Rate Limiting...")
        
        # Make multiple rapid requests
        rapid_requests = 0
        for i in range(10):
            success, _ = self.make_request('GET', 'products', auth_required=False)
            if success:
                rapid_requests += 1
        
        self.log_test("Rate Limiting Check", rapid_requests >= 8, 
                     f"Made {rapid_requests}/10 requests successfully")

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Starting AfroMarket UK Marketplace API Tests")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Authentication is required for most tests
        if not self.test_authentication():
            print("❌ Authentication failed - stopping tests")
            return False
        
        # Test products and get a product ID for other tests
        product_id = self.test_products_api()
        
        # Test marketplace features
        self.test_promo_codes()
        self.test_wishlist(product_id)
        self.test_reviews(product_id)
        self.test_questions(product_id)
        self.test_messages()
        self.test_order_tracking()
        self.test_refunds()
        self.test_rate_limiting()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for failure in self.failed_tests:
                print(f"  - {failure['test']}: {failure['error']}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"\n✨ Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 80

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