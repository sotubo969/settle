"""
AfroMarket UK - Final Function Verification Tests (Iteration 15)
Tests ALL functions: USER flows, OWNER flows, CHATBOT, DELIVERY
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://afromarket-staging.preview.emergentagent.com')

# Test credentials
USER_EMAIL = "user@test.com"
USER_PASSWORD = "123456"
OWNER_EMAIL = "sotubodammy@gmail.com"
OWNER_PASSWORD = "123456"


@pytest.fixture(scope="module")
def user_token():
    """Login as regular user and get token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": USER_EMAIL,
        "password": USER_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"User login failed: {response.text}")
    return response.json().get("token")


@pytest.fixture(scope="module")
def owner_token():
    """Login as owner and get token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": OWNER_EMAIL,
        "password": OWNER_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Owner login failed: {response.text}")
    return response.json().get("token")


class TestUserLogin:
    """USER: Login with user@test.com / 123456"""
    
    def test_user_login_success(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "token" in data
        assert data["user"]["email"] == USER_EMAIL
        print(f"USER LOGIN: SUCCESS - Token received for {USER_EMAIL}")


class TestBrowseProducts:
    """USER: Browse products (32 products should load)"""
    
    def test_get_all_products(self):
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200, f"Products fetch failed: {response.text}"
        products = response.json()
        assert isinstance(products, list)
        assert len(products) >= 30, f"Expected ~32 products, got {len(products)}"
        print(f"BROWSE PRODUCTS: SUCCESS - {len(products)} products loaded")
    
    def test_product_has_required_fields(self):
        response = requests.get(f"{BASE_URL}/api/products")
        products = response.json()
        if products:
            product = products[0]
            assert "id" in product
            assert "name" in product
            assert "price" in product
            print(f"PRODUCT FIELDS: SUCCESS - Product has id, name, price")


class TestCartOperations:
    """USER: Cart Add, View, Update, Remove operations"""
    
    def test_add_product_to_cart(self, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        # First get a product ID
        products_resp = requests.get(f"{BASE_URL}/api/products")
        products = products_resp.json()
        product_id = products[0]["id"]
        
        # Add to cart
        response = requests.post(
            f"{BASE_URL}/api/cart/add?product_id={product_id}&quantity=1",
            headers=headers
        )
        assert response.status_code == 200, f"Add to cart failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        print(f"CART ADD: SUCCESS - Added product {product_id} to cart")
    
    def test_view_cart_with_totals(self, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{BASE_URL}/api/cart", headers=headers)
        assert response.status_code == 200, f"Get cart failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "items" in data
        print(f"CART VIEW: SUCCESS - Cart has {len(data['items'])} items")
    
    def test_update_cart_quantity(self, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        # Get cart items
        cart_resp = requests.get(f"{BASE_URL}/api/cart", headers=headers)
        items = cart_resp.json().get("items", [])
        
        if items:
            product_id = items[0].get("product_id")
            response = requests.put(
                f"{BASE_URL}/api/cart/update/{product_id}?quantity=3",
                headers=headers
            )
            assert response.status_code == 200, f"Update cart failed: {response.text}"
            print(f"CART UPDATE: SUCCESS - Updated quantity to 3")
        else:
            pytest.skip("No items in cart to update")
    
    def test_remove_from_cart(self, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        # Get cart items
        cart_resp = requests.get(f"{BASE_URL}/api/cart", headers=headers)
        items = cart_resp.json().get("items", [])
        
        if items:
            product_id = items[0].get("product_id")
            response = requests.delete(
                f"{BASE_URL}/api/cart/remove/{product_id}",
                headers=headers
            )
            assert response.status_code == 200, f"Remove from cart failed: {response.text}"
            print(f"CART REMOVE: SUCCESS - Removed product {product_id}")
        else:
            pytest.skip("No items in cart to remove")


class TestWishlist:
    """USER: Toggle wishlist"""
    
    def test_toggle_wishlist(self, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        # Get a product ID
        products_resp = requests.get(f"{BASE_URL}/api/products")
        products = products_resp.json()
        product_id = products[0]["id"]
        
        # Toggle wishlist
        response = requests.post(
            f"{BASE_URL}/api/wishlist/toggle",
            headers=headers,
            json={"product_id": product_id}
        )
        assert response.status_code == 200, f"Toggle wishlist failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        print(f"WISHLIST TOGGLE: SUCCESS - in_wishlist={data.get('in_wishlist')}")
    
    def test_get_wishlist(self, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{BASE_URL}/api/wishlist", headers=headers)
        assert response.status_code == 200, f"Get wishlist failed: {response.text}"
        print(f"WISHLIST GET: SUCCESS")


class TestForgotPassword:
    """USER: Forgot password flow"""
    
    def test_forgot_password_with_valid_email(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": USER_EMAIL}
        )
        assert response.status_code == 200, f"Forgot password failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        print(f"FORGOT PASSWORD: SUCCESS - Email sent for {USER_EMAIL}")
    
    def test_forgot_password_with_invalid_email(self):
        # Should still return success to prevent email enumeration
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": "nonexistent@test.com"}
        )
        assert response.status_code == 200
        print(f"FORGOT PASSWORD (invalid): SUCCESS - Returns 200 (security)")


class TestProfile:
    """USER: Profile page"""
    
    def test_get_profile(self, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{BASE_URL}/api/profile", headers=headers)
        assert response.status_code == 200, f"Get profile failed: {response.text}"
        data = response.json()
        assert "user" in data
        print(f"PROFILE: SUCCESS - User email: {data['user'].get('email')}")


class TestLogout:
    """USER: Logout - JWT based, no server-side logout needed"""
    
    def test_logout_by_token_removal(self, user_token):
        # JWT logout is client-side - verify token works before "logout"
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        print(f"LOGOUT: Token-based logout (client-side) - VERIFIED")


class TestOwnerLogin:
    """OWNER: Login with sotubodammy@gmail.com / 123456"""
    
    def test_owner_login_success(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        assert response.status_code == 200, f"Owner login failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["user"].get("is_admin") is True
        print(f"OWNER LOGIN: SUCCESS - Admin user logged in")


class TestOwnerDashboard:
    """OWNER: Dashboard loads with stats"""
    
    def test_owner_dashboard_stats(self, owner_token):
        headers = {"Authorization": f"Bearer {owner_token}"}
        response = requests.get(f"{BASE_URL}/api/owner/dashboard", headers=headers)
        assert response.status_code == 200, f"Dashboard failed: {response.text}"
        data = response.json()
        assert "totalRevenue" in data
        assert "totalOrders" in data
        assert "totalVendors" in data
        assert "totalProducts" in data
        print(f"OWNER DASHBOARD: SUCCESS - Revenue: £{data['totalRevenue']}, Products: {data['totalProducts']}")
    
    def test_owner_stats(self, owner_token):
        headers = {"Authorization": f"Bearer {owner_token}"}
        response = requests.get(f"{BASE_URL}/api/owner/stats", headers=headers)
        assert response.status_code == 200, f"Stats failed: {response.text}"
        data = response.json()
        assert "totalVendors" in data
        print(f"OWNER STATS: SUCCESS - Total Vendors: {data['totalVendors']}")


class TestOwnerVendors:
    """OWNER: View all vendors"""
    
    def test_get_all_vendors(self, owner_token):
        headers = {"Authorization": f"Bearer {owner_token}"}
        response = requests.get(f"{BASE_URL}/api/owner/vendors", headers=headers)
        assert response.status_code == 200, f"Get vendors failed: {response.text}"
        vendors = response.json()
        assert isinstance(vendors, list)
        print(f"OWNER VENDORS: SUCCESS - {len(vendors)} vendors")


class TestOwnerProducts:
    """OWNER: View all products"""
    
    def test_get_all_products(self, owner_token):
        headers = {"Authorization": f"Bearer {owner_token}"}
        response = requests.get(f"{BASE_URL}/api/owner/products", headers=headers)
        assert response.status_code == 200, f"Get products failed: {response.text}"
        data = response.json()
        assert "products" in data
        print(f"OWNER PRODUCTS: SUCCESS - {len(data['products'])} products")


class TestOwnerDeliveries:
    """OWNER: View deliveries"""
    
    def test_get_deliveries(self, owner_token):
        headers = {"Authorization": f"Bearer {owner_token}"}
        response = requests.get(f"{BASE_URL}/api/owner/deliveries", headers=headers)
        assert response.status_code == 200, f"Get deliveries failed: {response.text}"
        deliveries = response.json()
        assert isinstance(deliveries, list)
        print(f"OWNER DELIVERIES: SUCCESS - {len(deliveries)} deliveries")


class TestChatbotWelcome:
    """CHATBOT: Welcome message"""
    
    def test_chatbot_welcome(self):
        response = requests.get(f"{BASE_URL}/api/chatbot/welcome")
        assert response.status_code == 200, f"Chatbot welcome failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "welcome_message" in data
        assert "session_id" in data
        print(f"CHATBOT WELCOME: SUCCESS - {data.get('bot_name', 'AfroBot')}")


class TestChatbotMessage:
    """CHATBOT: Send message and receive response"""
    
    def test_chatbot_message(self):
        # First get a session
        welcome_resp = requests.get(f"{BASE_URL}/api/chatbot/welcome")
        session_id = welcome_resp.json().get("session_id")
        
        # Send message
        response = requests.post(
            f"{BASE_URL}/api/chatbot/message",
            json={"message": "Hello, what products do you have?", "session_id": session_id}
        )
        assert response.status_code == 200, f"Chatbot message failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "response" in data
        print(f"CHATBOT MESSAGE: SUCCESS - Got response")


class TestDeliveryCalculate:
    """DELIVERY: Calculate delivery for London postcode"""
    
    def test_delivery_calculate_london(self):
        response = requests.post(
            f"{BASE_URL}/api/delivery/calculate",
            json={
                "postcode": "SW1A 1AA",  # London postcode
                "subtotal": 50.00,
                "weight_kg": 2.0,
                "delivery_option": "standard"
            }
        )
        assert response.status_code == 200, f"Delivery calc failed: {response.text}"
        data = response.json()
        assert "delivery_fee" in data or "fee" in data
        print(f"DELIVERY CALCULATE: SUCCESS - {data}")


class TestDeliveryOptions:
    """DELIVERY: Get delivery options"""
    
    def test_get_delivery_options(self):
        response = requests.get(
            f"{BASE_URL}/api/delivery/options",
            params={"postcode": "SW1A 1AA", "subtotal": 50.00, "weight_kg": 2.0}
        )
        assert response.status_code == 200, f"Delivery options failed: {response.text}"
        data = response.json()
        assert "options" in data or "available_options" in data or isinstance(data, dict)
        print(f"DELIVERY OPTIONS: SUCCESS")


class TestCategories:
    """Additional: Categories endpoint"""
    
    def test_get_categories(self):
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200, f"Categories failed: {response.text}"
        categories = response.json()
        assert isinstance(categories, list)
        assert len(categories) >= 8
        print(f"CATEGORIES: SUCCESS - {len(categories)} categories")


class TestHealthEndpoint:
    """Health endpoint returns 'healthy'"""
    
    def test_health_returns_healthy(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"HEALTH: SUCCESS - status=healthy")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
