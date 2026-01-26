#!/usr/bin/env python3
"""
Backend API Testing for AfroMarket Authentication System
Tests Firebase status and legacy authentication fallback
"""

import requests
import json
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://code-fetcher-23.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class AuthenticationTester:
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
        self.test_user = None
        self.test_user_id = None

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
            'name': test_name,
            'success': success,
            'details': details,
            'response_data': response_data,
            'timestamp': datetime.now().isoformat()
        })

    def test_firebase_status(self):
        """Test Firebase configuration status endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/auth/firebase/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                configured = data.get('configured', False)
                message = data.get('message', '')
                
                # Firebase should NOT be configured based on empty env vars
                if not configured and "not configured" in message.lower():
                    self.log_test("Firebase Status Check", True, f"Correctly reports not configured: {message}")
                    return True
                else:
                    self.log_test("Firebase Status Check", False, f"Unexpected status - configured: {configured}, message: {message}")
                    return False
            else:
                self.log_test("Firebase Status Check", False, f"Endpoint returned {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Firebase Status Check", False, f"Request failed: {str(e)}")
            return False

    def test_legacy_registration(self):
        """Test legacy user registration"""
        # Generate unique test user
        test_id = str(uuid.uuid4())[:8]
        self.test_user = {
            "name": f"Test User {test_id}",
            "email": f"testuser{test_id}@test.com",
            "password": "Test123!"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/register", 
                json=self.test_user,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('token') and data.get('user'):
                    user_data = data['user']
                    if (user_data.get('email') == self.test_user['email'] and 
                        user_data.get('name') == self.test_user['name'] and
                        user_data.get('role') == 'customer'):
                        
                        # Store token for subsequent tests
                        self.auth_token = data['token']
                        self.test_user_id = user_data['id']
                        self.log_test("Legacy Registration", True, f"User created successfully: {user_data['email']}")
                        return True
                    else:
                        self.log_test("Legacy Registration", False, "Invalid user data returned")
                        return False
                else:
                    self.log_test("Legacy Registration", False, f"Missing required fields in response: {data}")
                    return False
            else:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', error_msg)
                except:
                    pass
                self.log_test("Legacy Registration", False, f"Registration failed ({response.status_code}): {error_msg}")
                return False
                
        except Exception as e:
            self.log_test("Legacy Registration", False, f"Request failed: {str(e)}")
            return False

    def test_legacy_login(self):
        """Test legacy user login"""
        if not self.test_user:
            self.log_test("Legacy Login", False, "No test user available (registration failed)")
            return False
            
        try:
            login_data = {
                "email": self.test_user['email'],
                "password": self.test_user['password']
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('token') and data.get('user'):
                    user_data = data['user']
                    if (user_data.get('email') == login_data['email'] and
                        user_data.get('role') == 'customer'):
                        
                        self.log_test("Legacy Login", True, f"Login successful for: {user_data['email']}")
                        return True
                    else:
                        self.log_test("Legacy Login", False, "Invalid user data in login response")
                        return False
                else:
                    self.log_test("Legacy Login", False, f"Missing required fields in login response: {data}")
                    return False
            else:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', error_msg)
                except:
                    pass
                self.log_test("Legacy Login", False, f"Login failed ({response.status_code}): {error_msg}")
                return False
                
        except Exception as e:
            self.log_test("Legacy Login", False, f"Request failed: {str(e)}")
            return False

    def test_protected_endpoint(self):
        """Test accessing a protected endpoint with token"""
        if not self.auth_token:
            self.log_test("Protected Endpoint Access", False, "No token available")
            return False
            
        try:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            response = self.session.get(
                f"{API_BASE}/auth/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('email') and data.get('role'):
                    self.log_test("Protected Endpoint Access", True, f"Successfully accessed /auth/me: {data['email']}")
                    return True
                else:
                    self.log_test("Protected Endpoint Access", False, "Invalid response from protected endpoint")
                    return False
            else:
                self.log_test("Protected Endpoint Access", False, f"Failed to access protected endpoint ({response.status_code}): {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Protected Endpoint Access", False, f"Request failed: {str(e)}")
            return False

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        try:
            invalid_login = {
                "email": "nonexistent@test.com",
                "password": "wrongpassword"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=invalid_login,
                timeout=10
            )
            
            # Should return 401 for invalid credentials
            if response.status_code == 401:
                self.log_test("Invalid Login Rejection", True, "Correctly rejected invalid credentials")
                return True
            else:
                self.log_test("Invalid Login Rejection", False, f"Should reject invalid credentials with 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Login Rejection", False, f"Request failed: {str(e)}")
            return False

    def test_duplicate_registration(self):
        """Test registration with existing email"""
        if not self.test_user:
            self.log_test("Duplicate Registration Check", False, "No test user available")
            return False
            
        try:
            # Try to register with same email
            duplicate_user = {
                "name": "Another User",
                "email": self.test_user['email'],  # Same email
                "password": "DifferentPass123!"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/register",
                json=duplicate_user,
                timeout=10
            )
            
            # Should return 400 for duplicate email
            if response.status_code == 400:
                error_data = response.json()
                if "already registered" in error_data.get('detail', '').lower():
                    self.log_test("Duplicate Registration Check", True, "Correctly rejected duplicate email")
                    return True
                else:
                    self.log_test("Duplicate Registration Check", False, f"Wrong error message: {error_data.get('detail')}")
                    return False
            else:
                self.log_test("Duplicate Registration Check", False, f"Should reject duplicate email with 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Duplicate Registration Check", False, f"Request failed: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting AfroMarket Authentication Tests")
        print(f"📍 Testing against: {BACKEND_URL}")
        print("=" * 60)
        
        # Test Firebase status first
        self.test_firebase_status()
        
        # Test legacy authentication
        self.test_legacy_registration()
        self.test_legacy_login()
        self.test_protected_endpoint()
        
        # Test error cases
        self.test_invalid_login()
        self.test_duplicate_registration()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.test_results['passed_tests']}/{self.test_results['total_tests']} tests passed")
        
        if self.test_results['passed_tests'] == self.test_results['total_tests']:
            print("🎉 All tests passed! Authentication system working correctly.")
            return True
        else:
            print(f"⚠️  {self.test_results['failed_tests']} test(s) failed.")
            return False

def main():
    """Main test runner"""
    tester = AuthenticationTester()
    success = tester.run_all_tests()
    return 0 if success else 1
if __name__ == "__main__":
    sys.exit(main())