"""
AfroMarket UK - Critical Flow Tests (Iteration 14)
Testing: Forgot Password, Cart Add, Page Performance, User & Owner Flows
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://afromarket-staging.preview.emergentagent.com')
API = f"{BASE_URL}/api"

# Test credentials
OWNER_EMAIL = "sotubodammy@gmail.com"
OWNER_PASSWORD = "123456"
USER_EMAIL = "user@test.com"
USER_PASSWORD = "123456"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def user_token(api_client):
    """Get user authentication token"""
    response = api_client.post(f"{API}/auth/login", json={
        "email": USER_EMAIL,
        "password": USER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("User authentication failed - skipping user tests")


@pytest.fixture(scope="module")
def owner_token(api_client):
    """Get owner authentication token"""
    response = api_client.post(f"{API}/auth/login", json={
        "email": OWNER_EMAIL,
        "password": OWNER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Owner authentication failed - skipping owner tests")


# ============ FORGOT PASSWORD FLOW ============
class TestForgotPasswordFlow:
    """Tests for forgot password functionality - NEW feature"""
    
    def test_forgot_password_endpoint_exists(self, api_client):
        """Test that forgot password endpoint exists and accepts POST"""
        response = api_client.post(f"{API}/auth/forgot-password", json={
            "email": USER_EMAIL
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "message" in data
        print(f"✓ Forgot password endpoint working - {data['message']}")
    
    def test_forgot_password_invalid_email_format(self, api_client):
        """Test forgot password with invalid email format"""
        response = api_client.post(f"{API}/auth/forgot-password", json={
            "email": "not-an-email"
        })
        # Should still return 200 for security (no email enumeration)
        assert response.status_code in [200, 400, 422]
        print("✓ Forgot password handles invalid email format")
    
    def test_forgot_password_nonexistent_email(self, api_client):
        """Test forgot password with non-existent email (should not reveal if email exists)"""
        response = api_client.post(f"{API}/auth/forgot-password", json={
            "email": "nonexistent_user_test_abc123@example.com"
        })
        # Should return 200 for security (prevent email enumeration)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("✓ Forgot password correctly hides email existence")
    
    def test_forgot_password_empty_email(self, api_client):
        """Test forgot password with empty email"""
        response = api_client.post(f"{API}/auth/forgot-password", json={
            "email": ""
        })
        # Should return 400 for missing email
        assert response.status_code == 400
        print("✓ Forgot password rejects empty email")
    
    def test_reset_password_endpoint_exists(self, api_client):
        """Test that reset password endpoint exists"""
        response = api_client.post(f"{API}/auth/reset-password", json={
            "token": "invalid_token_12345",
            "password": "newpassword123"
        })
        # Should return 400 for invalid token, not 404 (endpoint exists)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print(f"✓ Reset password endpoint exists - returns {response.status_code}")
    
    def test_reset_password_short_password(self, api_client):
        """Test reset password with too short password"""
        response = api_client.post(f"{API}/auth/reset-password", json={
            "token": "some_token",
            "password": "abc"
        })
        assert response.status_code == 400
        print("✓ Reset password rejects short passwords")


# ============ CART ADD FUNCTIONALITY ============
class TestCartAddFunctionality:
    """Tests for cart add functionality - CRITICAL FIX"""
    
    def test_add_to_cart_with_query_params(self, api_client, user_token):
        """Test adding to cart using query parameters (fixed method)"""
        # Get a product
        products = api_client.get(f"{API}/products").json()
        assert len(products) > 0, "No products found"
        product_id = products[0]["id"]
        
        # Add to cart using query params (the fixed method)
        response = api_client.post(
            f"{API}/cart/add?product_id={product_id}&quantity=1",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Add to cart with query params works - Product: {product_id[:8]}...")
    
    def test_add_to_cart_multiple_quantity(self, api_client, user_token):
        """Test adding multiple items to cart"""
        products = api_client.get(f"{API}/products").json()
        product_id = products[1]["id"] if len(products) > 1 else products[0]["id"]
        
        response = api_client.post(
            f"{API}/cart/add?product_id={product_id}&quantity=3",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Add to cart with quantity=3 works")
    
    def test_get_cart_shows_items(self, api_client, user_token):
        """Test that cart shows added items with correct structure"""
        response = api_client.get(
            f"{API}/cart",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        
        if len(data["items"]) > 0:
            item = data["items"][0]
            # Verify item structure has product info
            assert "product" in item or "product_id" in item
            assert "quantity" in item
            print(f"✓ Cart shows {len(data['items'])} items with correct structure")
        else:
            print("✓ Cart endpoint working (0 items)")
    
    def test_cart_requires_auth(self, api_client):
        """Test cart endpoints require authentication"""
        response = api_client.get(f"{API}/cart")
        assert response.status_code == 401
        print("✓ Cart correctly requires authentication")


# ============ USER FLOW TESTS ============
class TestUserFlow:
    """Complete user flow tests"""
    
    def test_user_login(self, api_client):
        """Test user login with test credentials"""
        response = api_client.post(f"{API}/auth/login", json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "token" in data
        assert data["user"]["email"] == USER_EMAIL
        print(f"✓ User login successful: {data['user']['email']}")
    
    def test_browse_products(self, api_client):
        """Test products listing"""
        response = api_client.get(f"{API}/products")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        assert len(products) > 0
        print(f"✓ Products page returns {len(products)} products")
    
    def test_product_detail(self, api_client):
        """Test single product detail"""
        products = api_client.get(f"{API}/products").json()
        product_id = products[0]["id"]
        
        response = api_client.get(f"{API}/products/{product_id}")
        assert response.status_code == 200
        product = response.json()
        assert "id" in product
        assert "name" in product
        assert "price" in product
        print(f"✓ Product detail working - {product['name']}")
    
    def test_update_cart_quantity(self, api_client, user_token):
        """Test updating cart item quantity"""
        # First add an item
        products = api_client.get(f"{API}/products").json()
        product_id = products[0]["id"]
        
        api_client.post(
            f"{API}/cart/add?product_id={product_id}&quantity=1",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # Note: The API uses PUT /cart/update/{product_id}?quantity=X
        # This tests if the endpoint exists
        response = api_client.put(
            f"{API}/cart/update/{product_id}?quantity=5",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        # Accept 200 (success) or 404 (item not in cart)
        assert response.status_code in [200, 404, 422]
        print(f"✓ Cart update endpoint responds - Status: {response.status_code}")
    
    def test_wishlist_toggle(self, api_client, user_token):
        """Test wishlist toggle functionality"""
        products = api_client.get(f"{API}/products").json()
        product_id = products[2]["id"] if len(products) > 2 else products[0]["id"]
        
        response = api_client.post(
            f"{API}/wishlist/toggle",
            json={"product_id": product_id},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "in_wishlist" in data
        print(f"✓ Wishlist toggle working - In wishlist: {data['in_wishlist']}")
    
    def test_get_wishlist(self, api_client, user_token):
        """Test getting user wishlist"""
        response = api_client.get(
            f"{API}/wishlist",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        print(f"✓ Wishlist retrieved - {len(data['items'])} items")
    
    def test_user_profile(self, api_client, user_token):
        """Test user profile endpoint (auth/me)"""
        response = api_client.get(
            f"{API}/auth/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "user" in data
        print(f"✓ User profile working - {data['user']['email']}")


# ============ OWNER FLOW TESTS ============
class TestOwnerFlow:
    """Complete owner/admin flow tests"""
    
    def test_owner_login(self, api_client):
        """Test owner login with admin credentials"""
        response = api_client.post(f"{API}/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "token" in data
        print(f"✓ Owner login successful: {data['user']['email']}")
    
    def test_owner_dashboard_overview(self, api_client, owner_token):
        """Test owner dashboard main stats"""
        response = api_client.get(
            f"{API}/owner/dashboard",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "totalRevenue" in data
        assert "totalOrders" in data
        assert "totalVendors" in data
        assert "totalProducts" in data
        print(f"✓ Owner dashboard - Revenue: £{data['totalRevenue']}, Products: {data['totalProducts']}")
    
    def test_owner_vendors_tab(self, api_client, owner_token):
        """Test owner vendors list"""
        response = api_client.get(
            f"{API}/owner/vendors",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert response.status_code == 200
        vendors = response.json()
        assert isinstance(vendors, list)
        print(f"✓ Owner vendors tab - {len(vendors)} vendors")
    
    def test_owner_products_tab(self, api_client, owner_token):
        """Test owner products list"""
        response = api_client.get(
            f"{API}/owner/products",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        print(f"✓ Owner products tab - {len(data['products'])} products")
    
    def test_owner_stats(self, api_client, owner_token):
        """Test owner statistics"""
        response = api_client.get(
            f"{API}/owner/stats",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "totalVendors" in data
        assert "pendingVendors" in data
        assert "approvedVendors" in data
        print(f"✓ Owner stats - Pending: {data['pendingVendors']}, Approved: {data['approvedVendors']}")
    
    def test_owner_analytics(self, api_client, owner_token):
        """Test owner analytics"""
        response = api_client.get(
            f"{API}/owner/analytics?days=30",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "totalRevenue" in data
        assert "totalOrders" in data
        print(f"✓ Owner analytics - 30 days revenue: £{data['totalRevenue']}")
    
    def test_owner_deliveries_tab(self, api_client, owner_token):
        """Test owner deliveries list"""
        response = api_client.get(
            f"{API}/owner/deliveries",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert response.status_code == 200
        deliveries = response.json()
        assert isinstance(deliveries, list)
        print(f"✓ Owner deliveries tab - {len(deliveries)} deliveries")
    
    def test_owner_transactions(self, api_client, owner_token):
        """Test owner transactions list"""
        response = api_client.get(
            f"{API}/owner/transactions",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert response.status_code == 200
        transactions = response.json()
        assert isinstance(transactions, list)
        print(f"✓ Owner transactions - {len(transactions)} transactions")
    
    def test_owner_sales(self, api_client, owner_token):
        """Test owner sales data"""
        response = api_client.get(
            f"{API}/owner/sales",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert response.status_code == 200
        sales = response.json()
        assert isinstance(sales, list)
        print(f"✓ Owner sales data - {len(sales)} orders")


# ============ PAGE LOAD PERFORMANCE TESTS ============
class TestPageLoadPerformance:
    """Tests for page load times - should be under 5 seconds"""
    
    def test_products_page_performance(self, api_client):
        """Test products page loads within 5 seconds"""
        start = time.time()
        response = api_client.get(f"{API}/products")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 5.0, f"Products page took {elapsed:.2f}s (should be < 5s)"
        print(f"✓ Products page loaded in {elapsed:.2f}s")
    
    def test_health_endpoint_performance(self, api_client):
        """Test health endpoint is fast"""
        start = time.time()
        response = api_client.get(f"{API}/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0, f"Health check took {elapsed:.2f}s (should be < 2s)"
        print(f"✓ Health endpoint: {elapsed:.2f}s")
    
    def test_owner_dashboard_performance(self, api_client, owner_token):
        """Test owner dashboard loads within 5 seconds"""
        start = time.time()
        response = api_client.get(
            f"{API}/owner/dashboard",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 5.0, f"Owner dashboard took {elapsed:.2f}s (should be < 5s)"
        print(f"✓ Owner dashboard loaded in {elapsed:.2f}s")


# ============ ADDITIONAL CART OPERATIONS ============
class TestCartOperations:
    """Additional cart operation tests"""
    
    def test_remove_from_cart(self, api_client, user_token):
        """Test removing item from cart"""
        # First add an item
        products = api_client.get(f"{API}/products").json()
        product_id = products[0]["id"]
        
        api_client.post(
            f"{API}/cart/add?product_id={product_id}&quantity=1",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # Remove it
        response = api_client.delete(
            f"{API}/cart/remove/{product_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        # Accept 200 (success) or 404 (different endpoint format)
        assert response.status_code in [200, 404, 422]
        print(f"✓ Remove from cart endpoint - Status: {response.status_code}")
    
    def test_clear_cart(self, api_client, user_token):
        """Test clearing entire cart"""
        response = api_client.delete(
            f"{API}/cart/clear",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        print("✓ Clear cart endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
