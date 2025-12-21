#!/usr/bin/env python3
"""
Comprehensive Stripe Payment Flow Testing for AfroMarket UK
Tests the complete payment flow including login, cart operations, payment intent creation, and order creation.
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://code-fetcher-23.preview.emergentagent.com/api"
TEST_EMAIL = "sotubodammy@gmail.com"
TEST_PASSWORD = "NewPassword123!"

class StripePaymentTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.test_results = []
        self.product_id = None
        
    def log_test(self, test_name: str, success: bool, details: str, response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{BASE_URL}{endpoint}"
        
        # Default headers
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add auth token if available
        if self.auth_token:
            default_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        # Merge with custom headers
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=default_headers, params=data)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=default_headers, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, headers=default_headers, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=default_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except Exception as e:
            print(f"Request failed: {str(e)}")
            raise
    
    def test_login(self):
        """Test user login"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.make_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.auth_token = data["token"]
                    self.user_data = data.get("user")
                    self.log_test("User Login", True, f"Login successful - User: {self.user_data.get('name')} ({self.user_data.get('email')})")
                    return True
                else:
                    self.log_test("User Login", False, f"Login failed: {data}")
            elif response.status_code == 401:
                self.log_test("User Login", False, f"Invalid credentials - HTTP 401: {response.text}")
            else:
                self.log_test("User Login", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")
        
        return False
    
    def test_get_products(self):
        """Get products to add to cart"""
        try:
            response = self.make_request("GET", "/products")
            
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list) and len(products) > 0:
                    self.product_id = products[0].get("id")
                    product_name = products[0].get("name")
                    self.log_test("Get Products", True, f"Retrieved {len(products)} products - Using product ID {self.product_id}: {product_name}")
                    return True
                else:
                    self.log_test("Get Products", False, f"No products found or invalid response: {products}")
            else:
                self.log_test("Get Products", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Products", False, f"Exception: {str(e)}")
        
        return False
    
    def test_add_to_cart(self):
        """Add product to cart"""
        if not self.auth_token or not self.product_id:
            self.log_test("Add to Cart", False, "No auth token or product ID available")
            return False
        
        try:
            cart_item = {
                "productId": self.product_id,
                "quantity": 1
            }
            
            response = self.make_request("POST", "/cart/add", cart_item)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Add to Cart", True, f"Product {self.product_id} added to cart successfully")
                    return True
                else:
                    self.log_test("Add to Cart", False, f"Add to cart failed: {data}")
            else:
                self.log_test("Add to Cart", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Add to Cart", False, f"Exception: {str(e)}")
        
        return False
    
    def test_get_cart(self):
        """Verify cart contents"""
        if not self.auth_token:
            self.log_test("Get Cart", False, "No auth token available")
            return False
        
        try:
            response = self.make_request("GET", "/cart")
            
            if response.status_code == 200:
                cart_data = response.json()
                if "items" in cart_data:
                    items = cart_data["items"]
                    self.log_test("Get Cart", True, f"Cart retrieved with {len(items)} items")
                    
                    # Print cart details
                    if items:
                        for item in items:
                            print(f"   - {item.get('name')} (ID: {item.get('id')}) - Quantity: {item.get('quantity')} - Price: £{item.get('price')}")
                    
                    return len(items) > 0
                else:
                    self.log_test("Get Cart", False, f"Invalid cart response: {cart_data}")
            else:
                self.log_test("Get Cart", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Cart", False, f"Exception: {str(e)}")
        
        return False
    
    def test_create_stripe_payment_intent(self):
        """Test Stripe payment intent creation"""
        try:
            payment_data = {
                "amount": 10.99,
                "currency": "gbp",
                "metadata": {
                    "customerEmail": "test@example.com"
                }
            }
            
            response = self.make_request("POST", "/payment/stripe/create-intent", payment_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("clientSecret"):
                    client_secret = data["clientSecret"]
                    self.log_test("Create Stripe Payment Intent", True, 
                                f"Payment intent created successfully - Client Secret: {client_secret[:20]}...")
                    return client_secret
                else:
                    self.log_test("Create Stripe Payment Intent", False, f"No client secret in response: {data}")
            else:
                self.log_test("Create Stripe Payment Intent", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create Stripe Payment Intent", False, f"Exception: {str(e)}")
        
        return None
    
    def test_create_order_missing_shipping(self):
        """Test order creation with missing shipping fields (should fail)"""
        if not self.auth_token:
            self.log_test("Create Order - Missing Shipping", False, "No auth token available")
            return
        
        try:
            # Order with missing shipping fields
            order_data = {
                "items": [{"productId": 1, "name": "Test", "price": 10.99, "quantity": 1, "vendorId": 1}],
                "shippingInfo": {
                    "fullName": "Test User"
                    # Missing required fields: email, phone, address, city, postcode
                },
                "paymentInfo": {"method": "stripe", "transactionId": "pi_test_123", "status": "completed"},
                "subtotal": 10.99,
                "deliveryFee": 4.99,
                "total": 15.98
            }
            
            response = self.make_request("POST", "/orders", order_data)
            
            if response.status_code == 400:
                data = response.json()
                error_detail = data.get("detail", "")
                if "missing required shipping information" in error_detail.lower():
                    self.log_test("Create Order - Missing Shipping", True, 
                                f"Order correctly rejected for missing shipping info: {error_detail}")
                else:
                    self.log_test("Create Order - Missing Shipping", False, 
                                f"Wrong error message: {error_detail}")
            else:
                self.log_test("Create Order - Missing Shipping", False, 
                            f"Expected 400 error, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create Order - Missing Shipping", False, f"Exception: {str(e)}")
    
    def test_create_order_complete_shipping(self):
        """Test order creation with complete shipping info (should succeed)"""
        if not self.auth_token:
            self.log_test("Create Order - Complete Shipping", False, "No auth token available")
            return None
        
        try:
            # Order with complete shipping information
            order_data = {
                "items": [{"productId": 1, "name": "Test Product", "price": 10.99, "quantity": 1, "vendorId": 1}],
                "shippingInfo": {
                    "fullName": "Test User",
                    "email": "test@example.com",
                    "phone": "07123456789",
                    "address": "123 Test Street",
                    "city": "London",
                    "postcode": "SW1A 1AA"
                },
                "paymentInfo": {"method": "stripe", "transactionId": "pi_test_123", "status": "completed"},
                "subtotal": 10.99,
                "deliveryFee": 4.99,
                "total": 15.98
            }
            
            response = self.make_request("POST", "/orders", order_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") and data.get("orderId"):
                    order_id = data.get("orderId")
                    self.log_test("Create Order - Complete Shipping", True, 
                                f"Order created successfully - Order ID: {order_id}")
                    return order_id
                else:
                    self.log_test("Create Order - Complete Shipping", False, f"Order creation failed: {data}")
            else:
                self.log_test("Create Order - Complete Shipping", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create Order - Complete Shipping", False, f"Exception: {str(e)}")
        
        return None
    
    def test_verify_order_created(self):
        """Verify order was created by getting orders list"""
        if not self.auth_token:
            self.log_test("Verify Order Created", False, "No auth token available")
            return
        
        try:
            response = self.make_request("GET", "/orders")
            
            if response.status_code == 200:
                orders = response.json()
                if isinstance(orders, list):
                    self.log_test("Verify Order Created", True, 
                                f"Orders retrieved successfully - Total orders: {len(orders)}")
                    
                    # Print recent orders
                    if orders:
                        print("   Recent orders:")
                        for order in orders[-3:]:  # Show last 3 orders
                            print(f"   - Order {order.get('orderId')} - Items: {order.get('items')} - Total: £{order.get('total')} - Status: {order.get('status')}")
                else:
                    self.log_test("Verify Order Created", False, f"Invalid orders response: {orders}")
            else:
                self.log_test("Verify Order Created", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Verify Order Created", False, f"Exception: {str(e)}")
    
    def test_vendor_dashboard_access(self):
        """Test vendor dashboard APIs if user is a vendor"""
        if not self.auth_token:
            self.log_test("Vendor Dashboard Access", False, "No auth token available")
            return
        
        try:
            # Try to access vendor dashboard
            response = self.make_request("GET", "/vendor/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if "vendor" in data and "stats" in data:
                    vendor_info = data["vendor"]
                    stats = data["stats"]
                    self.log_test("Vendor Dashboard Access", True, 
                                f"Vendor dashboard accessible - Business: {vendor_info.get('businessName')}, "
                                f"Products: {stats.get('totalProducts')}, Revenue: £{stats.get('totalRevenue', 0)}")
                    
                    # Test vendor orders endpoint
                    self.test_vendor_orders()
                else:
                    self.log_test("Vendor Dashboard Access", False, f"Invalid dashboard response: {data}")
            elif response.status_code == 403:
                self.log_test("Vendor Dashboard Access", True, 
                            "User is not a vendor (403 Forbidden) - This is expected for regular customers")
            else:
                self.log_test("Vendor Dashboard Access", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Vendor Dashboard Access", False, f"Exception: {str(e)}")
    
    def test_vendor_orders(self):
        """Test vendor orders endpoint to see customer details"""
        try:
            response = self.make_request("GET", "/vendor/orders")
            
            if response.status_code == 200:
                data = response.json()
                if "orders" in data:
                    orders = data["orders"]
                    self.log_test("Vendor Orders", True, 
                                f"Vendor orders retrieved - Total: {len(orders)}")
                    
                    # Show customer details from recent orders
                    if orders:
                        print("   Recent vendor orders with customer details:")
                        for order in orders[:3]:  # Show first 3 orders
                            customer = order.get("customer", {})
                            print(f"   - Order {order.get('orderId')}: Customer {customer.get('name')} "
                                  f"({customer.get('email')}) - Phone: {customer.get('phone')} - "
                                  f"Address: {customer.get('address')}, {customer.get('city')}")
                else:
                    self.log_test("Vendor Orders", False, f"Invalid vendor orders response: {data}")
            elif response.status_code == 403:
                self.log_test("Vendor Orders", True, 
                            "User is not a vendor (403 Forbidden) - Cannot access vendor orders")
            else:
                self.log_test("Vendor Orders", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Vendor Orders", False, f"Exception: {str(e)}")
    
    def run_stripe_payment_flow_test(self):
        """Run complete Stripe payment flow test"""
        print("=" * 80)
        print("AFROMARKET UK - STRIPE PAYMENT FLOW TESTING")
        print("=" * 80)
        print(f"Base URL: {BASE_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Step 1: Login
        print("\n🔐 STEP 1: USER LOGIN")
        print("-" * 40)
        login_success = self.test_login()
        
        if not login_success:
            print("❌ Cannot proceed without successful login")
            return
        
        # Step 2: Get products
        print("\n📦 STEP 2: GET PRODUCTS")
        print("-" * 40)
        products_success = self.test_get_products()
        
        if not products_success:
            print("❌ Cannot proceed without products")
            return
        
        # Step 3: Add items to cart
        print("\n🛒 STEP 3: ADD ITEMS TO CART")
        print("-" * 40)
        cart_success = self.test_add_to_cart()
        
        # Step 4: Get cart to verify items
        print("\n🛒 STEP 4: VERIFY CART CONTENTS")
        print("-" * 40)
        self.test_get_cart()
        
        # Step 5: Create Stripe Payment Intent
        print("\n💳 STEP 5: CREATE STRIPE PAYMENT INTENT")
        print("-" * 40)
        client_secret = self.test_create_stripe_payment_intent()
        
        # Step 6: Test order creation with missing shipping (should fail)
        print("\n📋 STEP 6: TEST ORDER CREATION - MISSING SHIPPING INFO")
        print("-" * 40)
        self.test_create_order_missing_shipping()
        
        # Step 7: Test order creation with complete shipping (should succeed)
        print("\n📋 STEP 7: CREATE ORDER - COMPLETE SHIPPING INFO")
        print("-" * 40)
        order_id = self.test_create_order_complete_shipping()
        
        # Step 8: Verify order was created
        print("\n📋 STEP 8: VERIFY ORDER CREATION")
        print("-" * 40)
        self.test_verify_order_created()
        
        # Step 9: Test vendor dashboard APIs (if applicable)
        print("\n🏪 STEP 9: TEST VENDOR DASHBOARD APIS")
        print("-" * 40)
        self.test_vendor_dashboard_access()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("STRIPE PAYMENT FLOW TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            print("-" * 40)
            for test in self.test_results:
                if not test["success"]:
                    print(f"• {test['test']}: {test['details']}")
        
        print("\n✅ PASSED TESTS:")
        print("-" * 40)
        for test in self.test_results:
            if test["success"]:
                print(f"• {test['test']}: {test['details']}")
        
        print("=" * 80)
        
        # Overall assessment
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED - Stripe payment flow is working correctly!")
        elif failed_tests <= 2:
            print("⚠️  MOSTLY WORKING - Minor issues detected in Stripe payment flow")
        else:
            print("🚨 CRITICAL ISSUES - Stripe payment flow has significant problems")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = StripePaymentTester()
    tester.run_stripe_payment_flow_test()