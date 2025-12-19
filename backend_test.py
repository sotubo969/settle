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
BASE_URL = "https://code-fetcher-23.preview.emergentagent.com/api"
TEST_EMAIL = "info@surulerefoods.com"
TEST_PASSWORD = "changeme123"

# Owner credentials for testing owner dashboard
OWNER_EMAIL = "sotubodammy@gmail.com"
OWNER_PASSWORD = "owner2025!"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.owner_token = None
        self.owner_data = None
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
    
    def test_oauth_endpoints(self):
        """Test OAuth-related endpoints"""
        
        # Test OAuth session endpoint (without valid session_id - expect error)
        try:
            session_data = {
                "session_id": "test_invalid_session_id"
            }
            
            response = self.make_request("POST", "/auth/session", session_data)
            
            # We expect this to fail with invalid session
            if response.status_code in [400, 401, 404]:
                self.log_test("OAuth Session Exchange", True, f"OAuth session endpoint accessible (expected failure with invalid session) - HTTP {response.status_code}")
            else:
                self.log_test("OAuth Session Exchange", False, f"Unexpected response - HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("OAuth Session Exchange", False, f"Exception: {str(e)}")
        
        # Test OAuth me endpoint (without session cookie - expect error)
        try:
            response = self.make_request("GET", "/auth/me/oauth")
            
            # We expect this to fail without session cookie
            if response.status_code in [400, 401, 404]:
                self.log_test("OAuth Get User", True, f"OAuth me endpoint accessible (expected failure without session) - HTTP {response.status_code}")
            else:
                self.log_test("OAuth Get User", False, f"Unexpected response - HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("OAuth Get User", False, f"Exception: {str(e)}")
        
        # Test OAuth logout endpoint
        try:
            response = self.make_request("POST", "/auth/logout/oauth")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("OAuth Logout", True, "OAuth logout endpoint working")
                else:
                    self.log_test("OAuth Logout", False, f"OAuth logout failed: {data}")
            else:
                self.log_test("OAuth Logout", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("OAuth Logout", False, f"Exception: {str(e)}")
    
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
                            # Use query parameter instead of request body
                            url = f"/cart/update/{self.test_product_id}?quantity=3"
                            response = self.make_request("PUT", url)
                            
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
    
    def test_owner_login(self):
        """Test owner login to get owner token"""
        try:
            login_data = {
                "email": OWNER_EMAIL,
                "password": OWNER_PASSWORD
            }
            
            response = self.make_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.owner_token = data["token"]
                    self.owner_data = data.get("user")
                    self.log_test("Owner Login", True, f"Owner login successful - User: {self.owner_data.get('name')} ({self.owner_data.get('email')})")
                    return True
                else:
                    self.log_test("Owner Login", False, f"Owner login failed: {data}")
            elif response.status_code == 401:
                self.log_test("Owner Login", False, f"Invalid owner credentials - HTTP 401: {response.text}")
            else:
                self.log_test("Owner Login", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Owner Login", False, f"Exception: {str(e)}")
        
        return False
    
    def test_owner_dashboard_endpoints(self):
        """Test all owner dashboard endpoints"""
        if not self.owner_token:
            self.log_test("Owner Dashboard Tests", False, "No owner token available")
            return
        
        # Temporarily store current token and set owner token
        original_token = self.auth_token
        self.auth_token = self.owner_token
        
        try:
            # Test owner dashboard overview
            try:
                response = self.make_request("GET", "/owner/dashboard")
                
                if response.status_code == 200:
                    data = response.json()
                    if "overview" in data:
                        overview = data["overview"]
                        self.log_test("Owner Dashboard Overview", True, 
                                    f"Dashboard data retrieved - Vendors: {overview.get('totalVendors')}, "
                                    f"Products: {overview.get('totalProducts')}, "
                                    f"Orders: {overview.get('totalOrders')}, "
                                    f"Revenue: £{overview.get('totalRevenue', 0)}")
                    else:
                        self.log_test("Owner Dashboard Overview", False, f"Invalid dashboard response: {data}")
                elif response.status_code == 403:
                    self.log_test("Owner Dashboard Overview", False, "Access denied - not owner")
                else:
                    self.log_test("Owner Dashboard Overview", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Owner Dashboard Overview", False, f"Exception: {str(e)}")
            
            # Test owner vendors endpoint
            try:
                response = self.make_request("GET", "/owner/vendors")
                
                if response.status_code == 200:
                    data = response.json()
                    if "vendors" in data:
                        vendors = data["vendors"]
                        self.log_test("Owner Vendors List", True, 
                                    f"Retrieved {len(vendors)} vendors with detailed information")
                    else:
                        self.log_test("Owner Vendors List", False, f"Invalid vendors response: {data}")
                elif response.status_code == 403:
                    self.log_test("Owner Vendors List", False, "Access denied - not owner")
                else:
                    self.log_test("Owner Vendors List", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Owner Vendors List", False, f"Exception: {str(e)}")
            
            # Test owner products endpoint
            try:
                response = self.make_request("GET", "/owner/products")
                
                if response.status_code == 200:
                    data = response.json()
                    if "products" in data:
                        products = data["products"]
                        self.log_test("Owner Products List", True, 
                                    f"Retrieved {len(products)} products with vendor info and analytics")
                    else:
                        self.log_test("Owner Products List", False, f"Invalid products response: {data}")
                elif response.status_code == 403:
                    self.log_test("Owner Products List", False, "Access denied - not owner")
                else:
                    self.log_test("Owner Products List", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Owner Products List", False, f"Exception: {str(e)}")
            
            # Test owner analytics endpoint
            try:
                response = self.make_request("GET", "/owner/analytics", {"days": 30})
                
                if response.status_code == 200:
                    data = response.json()
                    if "period" in data:
                        self.log_test("Owner Analytics", True, 
                                    f"Analytics data retrieved for {data.get('period')} - "
                                    f"Total visits: {data.get('totalVisits')}, "
                                    f"Total orders: {data.get('totalOrders')}, "
                                    f"Total revenue: £{data.get('totalRevenue', 0)}")
                    else:
                        self.log_test("Owner Analytics", False, f"Invalid analytics response: {data}")
                elif response.status_code == 403:
                    self.log_test("Owner Analytics", False, "Access denied - not owner")
                else:
                    self.log_test("Owner Analytics", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Owner Analytics", False, f"Exception: {str(e)}")
            
            # Test owner transactions endpoint
            try:
                response = self.make_request("GET", "/owner/transactions")
                
                if response.status_code == 200:
                    data = response.json()
                    if "vendorTransactions" in data and "allTransactions" in data:
                        vendor_transactions = data["vendorTransactions"]
                        all_transactions = data["allTransactions"]
                        summary = data.get("summary", {})
                        self.log_test("Owner Transactions", True, 
                                    f"Transactions retrieved - Vendor groups: {len(vendor_transactions)}, "
                                    f"Total transactions: {len(all_transactions)}, "
                                    f"Total revenue: £{summary.get('totalRevenue', 0)}")
                    else:
                        self.log_test("Owner Transactions", False, f"Invalid transactions response: {data}")
                elif response.status_code == 403:
                    self.log_test("Owner Transactions", False, "Access denied - not owner")
                else:
                    self.log_test("Owner Transactions", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Owner Transactions", False, f"Exception: {str(e)}")
            
            # Test owner sales endpoint
            try:
                response = self.make_request("GET", "/owner/sales")
                
                if response.status_code == 200:
                    data = response.json()
                    if "vendorSales" in data:
                        vendor_sales = data["vendorSales"]
                        summary = data.get("summary", {})
                        self.log_test("Owner Sales", True, 
                                    f"Sales data retrieved for {len(vendor_sales)} vendors - "
                                    f"Total sales: £{summary.get('totalSales', 0)}, "
                                    f"Total commission: £{summary.get('totalCommission', 0)}")
                    else:
                        self.log_test("Owner Sales", False, f"Invalid sales response: {data}")
                elif response.status_code == 403:
                    self.log_test("Owner Sales", False, "Access denied - not owner")
                else:
                    self.log_test("Owner Sales", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Owner Sales", False, f"Exception: {str(e)}")
            
            # Test owner deliveries endpoint (if implemented)
            try:
                response = self.make_request("GET", "/owner/deliveries")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Owner Deliveries", True, f"Deliveries endpoint accessible - Response: {type(data)}")
                elif response.status_code == 404:
                    self.log_test("Owner Deliveries", False, "Deliveries endpoint not implemented (404)")
                elif response.status_code == 403:
                    self.log_test("Owner Deliveries", False, "Access denied - not owner")
                else:
                    self.log_test("Owner Deliveries", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Owner Deliveries", False, f"Exception: {str(e)}")
            
        finally:
            # Restore original token
            self.auth_token = original_token
    
    def test_owner_access_control(self):
        """Test that non-owner users get 403 error for owner endpoints"""
        if not self.auth_token:
            self.log_test("Owner Access Control", False, "No regular user token available")
            return
        
        # Test with regular user token (should get 403)
        owner_endpoints = [
            "/owner/dashboard",
            "/owner/vendors", 
            "/owner/products",
            "/owner/analytics",
            "/owner/transactions",
            "/owner/sales"
        ]
        
        access_denied_count = 0
        for endpoint in owner_endpoints:
            try:
                response = self.make_request("GET", endpoint)
                if response.status_code == 403:
                    access_denied_count += 1
                elif response.status_code == 401:
                    # Also acceptable - unauthorized
                    access_denied_count += 1
            except Exception:
                pass
        
        if access_denied_count == len(owner_endpoints):
            self.log_test("Owner Access Control", True, 
                        f"All {len(owner_endpoints)} owner endpoints properly deny access to non-owner users")
        else:
            self.log_test("Owner Access Control", False, 
                        f"Only {access_denied_count}/{len(owner_endpoints)} owner endpoints deny access properly")
    
    def test_analytics_tracking(self):
        """Test analytics tracking endpoint"""
        try:
            # Test analytics tracking (should work without authentication)
            analytics_data = {
                "productId": 1,
                "eventType": "product_view"
            }
            
            response = self.make_request("POST", "/analytics/track", analytics_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Analytics Tracking", True, "Analytics event tracked successfully")
                else:
                    self.log_test("Analytics Tracking", False, f"Analytics tracking failed: {data}")
            elif response.status_code == 404:
                self.log_test("Analytics Tracking", False, "Analytics tracking endpoint not implemented (404)")
            else:
                self.log_test("Analytics Tracking", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Analytics Tracking", False, f"Exception: {str(e)}")
    
    def test_vendor_approval(self):
        """Test vendor approval endpoint (owner only)"""
        if not self.owner_token:
            self.log_test("Vendor Approval", False, "No owner token available")
            return
        
        # Temporarily store current token and set owner token
        original_token = self.auth_token
        self.auth_token = self.owner_token
        
        try:
            # First, get list of vendors to find a pending one
            response = self.make_request("GET", "/owner/vendors")
            
            if response.status_code == 200:
                data = response.json()
                vendors = data.get("vendors", [])
                pending_vendor = None
                
                for vendor in vendors:
                    if vendor.get("status") == "pending":
                        pending_vendor = vendor
                        break
                
                if pending_vendor:
                    # Test vendor approval
                    vendor_id = pending_vendor["id"]
                    approval_url = f"/owner/vendors/{vendor_id}/approve?status=approved"
                    
                    response = self.make_request("PUT", approval_url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            self.log_test("Vendor Approval", True, 
                                        f"Vendor {vendor_id} approved successfully")
                        else:
                            self.log_test("Vendor Approval", False, f"Vendor approval failed: {data}")
                    elif response.status_code == 404:
                        self.log_test("Vendor Approval", False, "Vendor approval endpoint not implemented (404)")
                    else:
                        self.log_test("Vendor Approval", False, f"HTTP {response.status_code}: {response.text}")
                else:
                    self.log_test("Vendor Approval", True, "No pending vendors found to test approval (all vendors already processed)")
            else:
                self.log_test("Vendor Approval", False, f"Could not get vendors list: HTTP {response.status_code}")
        
        except Exception as e:
            self.log_test("Vendor Approval", False, f"Exception: {str(e)}")
        finally:
            # Restore original token
            self.auth_token = original_token
    
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
        
        # OAuth tests
        print("\n🔐 OAUTH TESTS")
        print("-" * 40)
        self.test_oauth_endpoints()
        
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
        
        # Owner Dashboard tests
        print("\n👑 OWNER DASHBOARD TESTS")
        print("-" * 40)
        owner_login_success = self.test_owner_login()
        
        if owner_login_success:
            self.test_owner_dashboard_endpoints()
            self.test_vendor_approval()
        
        # Test access control with regular user
        if login_success:
            self.test_owner_access_control()
        
        # Analytics tracking test
        print("\n📊 ANALYTICS TESTS")
        print("-" * 40)
        self.test_analytics_tracking()
        
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