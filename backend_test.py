#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for AfroMarket UK
Tests all backend endpoints including authentication, products, cart, orders, and vendor functionality.
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://sourcecode-fetch.preview.emergentagent.com/api"
TEST_EMAIL = "info@surulerefoods.com"
TEST_PASSWORD = "changeme123"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.test_results = []
        
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
    
    def test_health_check(self):
        """Test API health endpoint"""
        try:
            response = self.make_request("GET", "/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    self.log_test("Health Check", True, f"API is running - {data.get('message', '')}")
                else:
                    self.log_test("Health Check", False, f"Unexpected response: {data}")
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        try:
            # Test with new user data
            test_user = {
                "name": "Test User Backend",
                "email": f"test.backend.{hash(TEST_EMAIL) % 10000}@example.com",
                "password": "testpassword123"
            }
            
            response = self.make_request("POST", "/auth/register", test_user)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.log_test("User Registration", True, f"User registered successfully - ID: {data.get('user', {}).get('id')}")
                else:
                    self.log_test("User Registration", False, f"Registration failed: {data}")
            else:
                self.log_test("User Registration", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
    
    def test_user_login(self):
        """Test user login endpoint"""
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
    
    def test_get_current_user(self):
        """Test get current user endpoint"""
        if not self.auth_token:
            self.log_test("Get Current User", False, "No auth token available")
            return
        
        try:
            response = self.make_request("GET", "/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") and data.get("email"):
                    self.log_test("Get Current User", True, f"User data retrieved - ID: {data.get('id')}, Email: {data.get('email')}")
                else:
                    self.log_test("Get Current User", False, f"Incomplete user data: {data}")
            else:
                self.log_test("Get Current User", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Current User", False, f"Exception: {str(e)}")
    
    def test_products_endpoints(self):
        """Test all product-related endpoints"""
        
        # Test get all products
        try:
            response = self.make_request("GET", "/products")
            
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list) and len(products) > 0:
                    self.log_test("Get All Products", True, f"Retrieved {len(products)} products")
                    
                    # Store first product for detail test
                    self.test_product_id = products[0].get("id")
                else:
                    self.log_test("Get All Products", False, f"No products found or invalid response: {products}")
            else:
                self.log_test("Get All Products", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get All Products", False, f"Exception: {str(e)}")
        
        # Test featured products
        try:
            response = self.make_request("GET", "/products", {"featured": "true"})
            
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list):
                    featured_count = len([p for p in products if p.get("featured")])
                    self.log_test("Get Featured Products", True, f"Retrieved {len(products)} products, {featured_count} marked as featured")
                else:
                    self.log_test("Get Featured Products", False, f"Invalid response: {products}")
            else:
                self.log_test("Get Featured Products", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Featured Products", False, f"Exception: {str(e)}")
        
        # Test category filter
        try:
            response = self.make_request("GET", "/products", {"category": "Fresh Produce"})
            
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list):
                    self.log_test("Get Products by Category", True, f"Retrieved {len(products)} products for 'Fresh Produce' category")
                else:
                    self.log_test("Get Products by Category", False, f"Invalid response: {products}")
            else:
                self.log_test("Get Products by Category", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Products by Category", False, f"Exception: {str(e)}")
        
        # Test search functionality
        try:
            response = self.make_request("GET", "/products", {"search": "rice"})
            
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list):
                    self.log_test("Search Products", True, f"Search for 'rice' returned {len(products)} products")
                else:
                    self.log_test("Search Products", False, f"Invalid response: {products}")
            else:
                self.log_test("Search Products", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Search Products", False, f"Exception: {str(e)}")
        
        # Test product detail
        if hasattr(self, 'test_product_id') and self.test_product_id:
            try:
                response = self.make_request("GET", f"/products/{self.test_product_id}")
                
                if response.status_code == 200:
                    product = response.json()
                    if product.get("id") == self.test_product_id:
                        self.log_test("Get Product Detail", True, f"Retrieved product details for ID {self.test_product_id}: {product.get('name')}")
                    else:
                        self.log_test("Get Product Detail", False, f"Product ID mismatch: {product}")
                else:
                    self.log_test("Get Product Detail", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Get Product Detail", False, f"Exception: {str(e)}")
    
    def test_cart_operations(self):
        """Test all cart-related endpoints"""
        if not self.auth_token:
            self.log_test("Cart Operations", False, "No auth token available")
            return
        
        # Test get cart (initially empty)
        try:
            response = self.make_request("GET", "/cart")
            
            if response.status_code == 200:
                cart_data = response.json()
                if "items" in cart_data:
                    self.log_test("Get Cart", True, f"Cart retrieved with {len(cart_data['items'])} items")
                else:
                    self.log_test("Get Cart", False, f"Invalid cart response: {cart_data}")
            else:
                self.log_test("Get Cart", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Cart", False, f"Exception: {str(e)}")
        
        # Test add to cart (need a product ID)
        if hasattr(self, 'test_product_id') and self.test_product_id:
            try:
                cart_item = {
                    "productId": self.test_product_id,
                    "quantity": 2
                }
                
                response = self.make_request("POST", "/cart/add", cart_item)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_test("Add to Cart", True, f"Product {self.test_product_id} added to cart successfully")
                        
                        # Test update cart quantity
                        try:
                            response = self.make_request("PUT", f"/cart/update/{self.test_product_id}", {"quantity": 3})
                            
                            if response.status_code == 200:
                                data = response.json()
                                if data.get("success"):
                                    self.log_test("Update Cart Quantity", True, f"Cart quantity updated for product {self.test_product_id}")
                                else:
                                    self.log_test("Update Cart Quantity", False, f"Update failed: {data}")
                            else:
                                self.log_test("Update Cart Quantity", False, f"HTTP {response.status_code}: {response.text}")
                        except Exception as e:
                            self.log_test("Update Cart Quantity", False, f"Exception: {str(e)}")
                        
                        # Test remove from cart
                        try:
                            response = self.make_request("DELETE", f"/cart/remove/{self.test_product_id}")
                            
                            if response.status_code == 200:
                                data = response.json()
                                if data.get("success"):
                                    self.log_test("Remove from Cart", True, f"Product {self.test_product_id} removed from cart")
                                else:
                                    self.log_test("Remove from Cart", False, f"Remove failed: {data}")
                            else:
                                self.log_test("Remove from Cart", False, f"HTTP {response.status_code}: {response.text}")
                        except Exception as e:
                            self.log_test("Remove from Cart", False, f"Exception: {str(e)}")
                        
                    else:
                        self.log_test("Add to Cart", False, f"Add to cart failed: {data}")
                else:
                    self.log_test("Add to Cart", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Add to Cart", False, f"Exception: {str(e)}")
        
        # Test clear cart
        try:
            response = self.make_request("DELETE", "/cart/clear")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Clear Cart", True, "Cart cleared successfully")
                else:
                    self.log_test("Clear Cart", False, f"Clear cart failed: {data}")
            else:
                self.log_test("Clear Cart", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Clear Cart", False, f"Exception: {str(e)}")
    
    def test_orders(self):
        """Test order-related endpoints"""
        if not self.auth_token:
            self.log_test("Orders", False, "No auth token available")
            return
        
        # Test get orders
        try:
            response = self.make_request("GET", "/orders")
            
            if response.status_code == 200:
                orders = response.json()
                if isinstance(orders, list):
                    self.log_test("Get Orders", True, f"Retrieved {len(orders)} orders")
                else:
                    self.log_test("Get Orders", False, f"Invalid orders response: {orders}")
            else:
                self.log_test("Get Orders", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Orders", False, f"Exception: {str(e)}")
        
        # Test create order (with sample data)
        try:
            order_data = {
                "items": [
                    {"productId": 1, "quantity": 1, "price": 10.99}
                ],
                "shippingInfo": {
                    "fullName": "Test User",
                    "address": "123 Test Street",
                    "city": "London",
                    "postcode": "SW1A 1AA",
                    "phone": "07123456789"
                },
                "paymentInfo": {
                    "method": "card",
                    "cardLast4": "1234"
                },
                "subtotal": 10.99,
                "deliveryFee": 3.99,
                "total": 14.98
            }
            
            response = self.make_request("POST", "/orders", order_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") and data.get("orderId"):
                    self.log_test("Create Order", True, f"Order created successfully - ID: {data.get('orderId')}")
                else:
                    self.log_test("Create Order", False, f"Order creation failed: {data}")
            else:
                self.log_test("Create Order", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create Order", False, f"Exception: {str(e)}")
    
    def test_vendor_registration(self):
        """Test vendor registration endpoint"""
        try:
            vendor_data = {
                "businessName": "Test Backend Vendor",
                "description": "A test vendor for backend API testing",
                "email": f"vendor.test.{hash(TEST_EMAIL) % 10000}@example.com",
                "phone": "07987654321",
                "address": "456 Vendor Street",
                "city": "Manchester",
                "postcode": "M1 1AA"
            }
            
            response = self.make_request("POST", "/vendors/register", vendor_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("vendor"):
                    self.log_test("Vendor Registration", True, f"Vendor registered successfully - ID: {data['vendor'].get('id')}")
                else:
                    self.log_test("Vendor Registration", False, f"Vendor registration failed: {data}")
            else:
                self.log_test("Vendor Registration", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Vendor Registration", False, f"Exception: {str(e)}")
    
    def test_profile_operations(self):
        """Test profile-related endpoints"""
        if not self.auth_token:
            self.log_test("Profile Operations", False, "No auth token available")
            return
        
        # Test profile update
        try:
            profile_data = {
                "name": "Updated Test User",
                "phone": "07111222333"
            }
            
            response = self.make_request("PUT", "/profile/update", profile_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("user"):
                    self.log_test("Update Profile", True, f"Profile updated successfully - Name: {data['user'].get('name')}")
                else:
                    self.log_test("Update Profile", False, f"Profile update failed: {data}")
            else:
                self.log_test("Update Profile", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Update Profile", False, f"Exception: {str(e)}")
        
        # Test add address
        try:
            address_data = {
                "fullName": "Test User",
                "address": "789 Test Avenue",
                "city": "Birmingham",
                "postcode": "B1 1AA",
                "phone": "07444555666",
                "isDefault": True
            }
            
            response = self.make_request("POST", "/profile/addresses", address_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Add Address", True, f"Address added successfully - Total addresses: {len(data.get('addresses', []))}")
                else:
                    self.log_test("Add Address", False, f"Add address failed: {data}")
            else:
                self.log_test("Add Address", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Add Address", False, f"Exception: {str(e)}")
    
    def test_wishlist_operations(self):
        """Test wishlist-related endpoints"""
        if not self.auth_token:
            self.log_test("Wishlist Operations", False, "No auth token available")
            return
        
        # Test get wishlist
        try:
            response = self.make_request("GET", "/wishlist")
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data:
                    self.log_test("Get Wishlist", True, f"Wishlist retrieved with {len(data['items'])} items")
                else:
                    self.log_test("Get Wishlist", False, f"Invalid wishlist response: {data}")
            else:
                self.log_test("Get Wishlist", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Wishlist", False, f"Exception: {str(e)}")
        
        # Test add to wishlist
        if hasattr(self, 'test_product_id') and self.test_product_id:
            try:
                response = self.make_request("POST", f"/wishlist/add/{self.test_product_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_test("Add to Wishlist", True, f"Product {self.test_product_id} added to wishlist")
                        
                        # Test remove from wishlist
                        try:
                            response = self.make_request("DELETE", f"/wishlist/remove/{self.test_product_id}")
                            
                            if response.status_code == 200:
                                data = response.json()
                                if data.get("success"):
                                    self.log_test("Remove from Wishlist", True, f"Product {self.test_product_id} removed from wishlist")
                                else:
                                    self.log_test("Remove from Wishlist", False, f"Remove failed: {data}")
                            else:
                                self.log_test("Remove from Wishlist", False, f"HTTP {response.status_code}: {response.text}")
                        except Exception as e:
                            self.log_test("Remove from Wishlist", False, f"Exception: {str(e)}")
                        
                    else:
                        self.log_test("Add to Wishlist", False, f"Add to wishlist failed: {data}")
                else:
                    self.log_test("Add to Wishlist", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Add to Wishlist", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 80)
        print("AFROMARKET UK - COMPREHENSIVE BACKEND API TESTING")
        print("=" * 80)
        print(f"Base URL: {BASE_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Health check first
        self.test_health_check()
        
        # Authentication tests
        print("\n🔐 AUTHENTICATION TESTS")
        print("-" * 40)
        self.test_user_registration()
        login_success = self.test_user_login()
        
        if login_success:
            self.test_get_current_user()
        
        # Product tests
        print("\n📦 PRODUCT TESTS")
        print("-" * 40)
        self.test_products_endpoints()
        
        # Cart tests (requires authentication)
        if login_success:
            print("\n🛒 CART TESTS")
            print("-" * 40)
            self.test_cart_operations()
        
        # Order tests (requires authentication)
        if login_success:
            print("\n📋 ORDER TESTS")
            print("-" * 40)
            self.test_orders()
        
        # Profile tests (requires authentication)
        if login_success:
            print("\n👤 PROFILE TESTS")
            print("-" * 40)
            self.test_profile_operations()
        
        # Wishlist tests (requires authentication)
        if login_success:
            print("\n❤️ WISHLIST TESTS")
            print("-" * 40)
            self.test_wishlist_operations()
        
        # Vendor tests
        print("\n🏪 VENDOR TESTS")
        print("-" * 40)
        self.test_vendor_registration()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
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

if __name__ == "__main__":
    tester = BackendTester()
    tester.run_all_tests()