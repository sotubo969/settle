"""
AfroMarket UK API Tests - Iteration 12
Testing: Vendor stock management, Wishlist toggle, Cart functionality,
         Order status tracking, Session persistence
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


class TestHealthAndBasicEndpoints:
    """Basic API health and endpoint tests"""
    
    def test_health_endpoint(self, api_client):
        """Test API health check"""
        response = api_client.get(f"{API}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "firestore"
        print("✓ Health endpoint working")
    
    def test_products_list(self, api_client):
        """Test products listing endpoint"""
        response = api_client.get(f"{API}/products")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        assert len(products) > 0
        
        # Verify product structure
        product = products[0]
        assert "id" in product
        assert "name" in product
        assert "price" in product
        print(f"✓ Products endpoint working - {len(products)} products found")


class TestAuthentication:
    """Authentication flow tests"""
    
    def test_user_login(self, api_client):
        """Test user login"""
        response = api_client.post(f"{API}/auth/login", json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == USER_EMAIL
        print(f"✓ User login successful: {data['user']['email']}")
    
    def test_owner_login(self, api_client):
        """Test owner login"""
        response = api_client.post(f"{API}/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "token" in data
        assert data["user"]["is_admin"] == True or data["user"]["email"] == OWNER_EMAIL
        print(f"✓ Owner login successful: {data['user']['email']}")
    
    def test_auth_me_endpoint(self, api_client, user_token):
        """Test current user info endpoint"""
        response = api_client.get(
            f"{API}/auth/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "user" in data
        print(f"✓ Auth/me endpoint working for user: {data['user']['email']}")


class TestCartFunctionality:
    """Cart operations tests"""
    
    def test_get_cart(self, api_client, user_token):
        """Test getting user cart"""
        response = api_client.get(
            f"{API}/cart",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        print(f"✓ Cart retrieved - {len(data['items'])} items")
    
    def test_add_to_cart(self, api_client, user_token):
        """Test adding item to cart"""
        # Get first product
        products = api_client.get(f"{API}/products").json()
        product_id = products[0]["id"]
        
        response = api_client.post(
            f"{API}/cart/add?product_id={product_id}&quantity=1",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Added product to cart: {product_id}")


class TestWishlistFunctionality:
    """Wishlist operations tests"""
    
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
    
    def test_wishlist_toggle(self, api_client, user_token):
        """Test toggling product in wishlist"""
        # Get first product
        products = api_client.get(f"{API}/products").json()
        product_id = products[0]["id"]
        
        # Toggle wishlist (add)
        response = api_client.post(
            f"{API}/wishlist/toggle",
            json={"product_id": product_id},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "in_wishlist" in data
        first_state = data["in_wishlist"]
        print(f"✓ Wishlist toggle - Product in wishlist: {first_state}")
        
        # Toggle again (should change state)
        response2 = api_client.post(
            f"{API}/wishlist/toggle",
            json={"product_id": product_id},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["in_wishlist"] != first_state
        print(f"✓ Wishlist toggle reversed - Product in wishlist: {data2['in_wishlist']}")


class TestOwnerDashboard:
    """Owner dashboard tests"""
    
    def test_owner_dashboard_access(self, api_client, owner_token):
        """Test owner dashboard endpoint"""
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
        print(f"✓ Owner dashboard accessible - {data['totalProducts']} products, {data['totalVendors']} vendors")
    
    def test_owner_stats(self, api_client, owner_token):
        """Test owner stats endpoint"""
        response = api_client.get(
            f"{API}/owner/stats",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "totalVendors" in data
        assert "pendingVendors" in data
        print(f"✓ Owner stats - Total vendors: {data['totalVendors']}, Pending: {data['pendingVendors']}")
    
    def test_owner_vendors_list(self, api_client, owner_token):
        """Test owner vendors listing"""
        response = api_client.get(
            f"{API}/owner/vendors",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert response.status_code == 200
        vendors = response.json()
        assert isinstance(vendors, list)
        print(f"✓ Owner vendors list - {len(vendors)} vendors")
    
    def test_owner_deliveries(self, api_client, owner_token):
        """Test owner deliveries endpoint"""
        response = api_client.get(
            f"{API}/owner/deliveries",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert response.status_code == 200
        deliveries = response.json()
        assert isinstance(deliveries, list)
        print(f"✓ Owner deliveries - {len(deliveries)} deliveries")


class TestVendorStockManagement:
    """Vendor stock management tests"""
    
    def test_vendor_dashboard_requires_auth(self, api_client):
        """Test vendor dashboard requires authentication"""
        response = api_client.get(f"{API}/vendor/dashboard")
        assert response.status_code == 401
        print("✓ Vendor dashboard correctly requires authentication")
    
    def test_vendor_products_requires_auth(self, api_client):
        """Test vendor products requires authentication"""
        response = api_client.get(f"{API}/vendor/products")
        assert response.status_code == 401
        print("✓ Vendor products correctly requires authentication")


class TestChatbot:
    """Chatbot API tests"""
    
    def test_chatbot_welcome(self, api_client):
        """Test chatbot welcome endpoint"""
        response = api_client.get(f"{API}/chatbot/welcome")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "welcome_message" in data
        assert "quick_replies" in data
        assert "session_id" in data
        print(f"✓ Chatbot welcome endpoint working - Session: {data['session_id'][:8]}...")
    
    def test_chatbot_message(self, api_client):
        """Test chatbot message endpoint"""
        # First get session ID
        welcome = api_client.get(f"{API}/chatbot/welcome").json()
        session_id = welcome["session_id"]
        
        # Send message
        response = api_client.post(
            f"{API}/chatbot/message",
            json={
                "message": "What products do you have?",
                "session_id": session_id
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "response" in data
        print(f"✓ Chatbot message response received")


class TestProductSearch:
    """Product search tests"""
    
    def test_search_products(self, api_client):
        """Test product search"""
        response = api_client.get(f"{API}/products?search=plantain")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        print(f"✓ Search for 'plantain' returned {len(products)} products")
    
    def test_category_filter(self, api_client):
        """Test category filter"""
        response = api_client.get(f"{API}/products?category=grains")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        print(f"✓ Category filter returned {len(products)} products")


class TestDeliveryService:
    """Delivery calculation tests"""
    
    def test_delivery_calculate(self, api_client):
        """Test delivery calculation"""
        response = api_client.post(
            f"{API}/delivery/calculate",
            json={
                "postcode": "E1 6AN",
                "subtotal": 50.0,
                "weight_kg": 2.0,
                "delivery_option": "standard"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "delivery_fee" in data or "fee" in data or "price" in data
        print(f"✓ Delivery calculation working")
    
    def test_delivery_zones(self, api_client):
        """Test delivery zones endpoint"""
        response = api_client.get(f"{API}/delivery/zones")
        assert response.status_code == 200
        data = response.json()
        assert "zones" in data
        print(f"✓ Delivery zones returned {len(data['zones'])} zones")


class TestPushNotifications:
    """Push notification tests"""
    
    def test_vapid_key_endpoint(self, api_client):
        """Test VAPID public key endpoint"""
        response = api_client.get(f"{API}/push/vapid-key")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "publicKey" in data
        print(f"✓ VAPID key endpoint working - Configured: {data['configured']}")


class TestVendorNotifications:
    """Vendor notification tests"""
    
    def test_notifications_by_email(self, api_client):
        """Test notifications by vendor email"""
        response = api_client.get(f"{API}/vendor/notifications/by-email/test@example.com")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Vendor notifications by email endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
