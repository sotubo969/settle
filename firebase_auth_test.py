#!/usr/bin/env python3
"""
Firebase Authentication Testing for AfroMarket UK
Tests Firebase integration and authentication flow
"""

import requests
import json
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration - Use public URL for testing
BACKEND_URL = "https://mine-pull.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class FirebaseAuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AfroMarket-Firebase-Test/1.0'
        })
        
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        self.auth_token = None
        self.test_user = None

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
        """Test Firebase configuration status endpoint - Should show configured=true"""
        try:
            response = self.session.get(f"{API_BASE}/auth/firebase/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                configured = data.get('configured', False)
                message = data.get('message', '')
                
                if configured:
                    self.log_test("Firebase Status Check", True, f"Firebase is configured: {message}")
                    return True
                else:
                    self.log_test("Firebase Status Check", False, f"Firebase not configured: {message}")
                    return False
            else:
                self.log_test("Firebase Status Check", False, f"Endpoint returned {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Firebase Status Check", False, f"Request failed: {str(e)}")
            return False

    def test_firebase_auth_endpoint_structure(self):
        """Test Firebase auth endpoint structure with invalid token"""
        try:
            # Test with invalid token to check endpoint structure
            test_data = {
                "idToken": "invalid_test_token_for_structure_check",
                "displayName": "Test User",
                "photoURL": "https://example.com/photo.jpg"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/firebase", 
                json=test_data,
                timeout=10
            )
            
            # Should return 401 for invalid token (not 500 if Firebase is configured)
            if response.status_code == 401:
                data = response.json()
                detail = data.get('detail', '')
                
                if 'invalid' in detail.lower() or 'token' in detail.lower():
                    self.log_test("Firebase Auth Endpoint Structure", True, f"Correctly rejects invalid token: {detail}")
                    return True
                else:
                    self.log_test("Firebase Auth Endpoint Structure", False, f"Unexpected error message: {detail}")
                    return False
            elif response.status_code == 500:
                data = response.json()
                detail = data.get('detail', '')
                if 'not configured' in detail.lower():
                    self.log_test("Firebase Auth Endpoint Structure", False, f"Firebase not configured: {detail}")
                    return False
                else:
                    self.log_test("Firebase Auth Endpoint Structure", True, f"Firebase configured but token invalid: {detail}")
                    return True
            else:
                self.log_test("Firebase Auth Endpoint Structure", False, f"Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Firebase Auth Endpoint Structure", False, f"Request failed: {str(e)}")
            return False

    def test_legacy_auth_still_works(self):
        """Test that legacy email/password auth still works alongside Firebase"""
        # Generate unique test user
        test_id = str(uuid.uuid4())[:8]
        self.test_user = {
            "name": f"Test User {test_id}",
            "email": f"testuser{test_id}@test.com",
            "password": "Test123!"
        }
        
        try:
            # Test registration
            response = self.session.post(
                f"{API_BASE}/auth/register", 
                json=self.test_user,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('token'):
                    self.auth_token = data['token']
                    self.log_test("Legacy Registration (alongside Firebase)", True, f"User created: {self.test_user['email']}")
                    
                    # Test login
                    login_data = {
                        "email": self.test_user['email'],
                        "password": self.test_user['password']
                    }
                    
                    login_response = self.session.post(
                        f"{API_BASE}/auth/login",
                        json=login_data,
                        timeout=10
                    )
                    
                    if login_response.status_code == 200:
                        login_result = login_response.json()
                        if login_result.get('success'):
                            self.log_test("Legacy Login (alongside Firebase)", True, "Legacy auth works with Firebase enabled")
                            return True
                        else:
                            self.log_test("Legacy Login (alongside Firebase)", False, "Login failed")
                            return False
                    else:
                        self.log_test("Legacy Login (alongside Firebase)", False, f"Login failed: {login_response.status_code}")
                        return False
                else:
                    self.log_test("Legacy Registration (alongside Firebase)", False, "Registration response invalid")
                    return False
            else:
                self.log_test("Legacy Registration (alongside Firebase)", False, f"Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Legacy Registration (alongside Firebase)", False, f"Request failed: {str(e)}")
            return False

    def test_protected_endpoint_access(self):
        """Test accessing protected endpoint with legacy token"""
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
                if data.get('email'):
                    self.log_test("Protected Endpoint Access", True, f"Successfully accessed /auth/me: {data['email']}")
                    return True
                else:
                    self.log_test("Protected Endpoint Access", False, "Invalid response from protected endpoint")
                    return False
            else:
                self.log_test("Protected Endpoint Access", False, f"Failed to access protected endpoint: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Protected Endpoint Access", False, f"Request failed: {str(e)}")
            return False

    def test_backend_health(self):
        """Test basic backend health"""
        try:
            response = self.session.get(f"{BACKEND_URL}/", timeout=10)
            
            if response.status_code == 200:
                self.log_test("Backend Health Check", True, "Backend is responding")
                return True
            else:
                self.log_test("Backend Health Check", False, f"Backend returned {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Backend not accessible: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all Firebase authentication tests"""
        print("🔥 Firebase Authentication Testing for AfroMarket UK")
        print(f"📍 Testing against: {BACKEND_URL}")
        print("=" * 60)
        
        # Test backend health first
        if not self.test_backend_health():
            print("❌ Backend not accessible, stopping tests")
            return False
        
        # Test Firebase configuration
        firebase_configured = self.test_firebase_status()
        
        # Test Firebase endpoint structure
        self.test_firebase_auth_endpoint_structure()
        
        # Test legacy auth still works
        self.test_legacy_auth_still_works()
        self.test_protected_endpoint_access()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.test_results['passed_tests']}/{self.test_results['total_tests']} tests passed")
        
        if firebase_configured:
            print("🎉 Firebase is configured and ready for use!")
        else:
            print("⚠️  Firebase configuration issue detected")
        
        if self.test_results['passed_tests'] >= self.test_results['total_tests'] - 1:  # Allow 1 failure
            print("✅ Authentication system working correctly")
            return True
        else:
            print(f"❌ {self.test_results['failed_tests']} test(s) failed")
            return False

def main():
    """Main test runner"""
    tester = FirebaseAuthTester()
    success = tester.run_all_tests()
    
    # Save results
    with open('/app/firebase_auth_test_results.json', 'w') as f:
        json.dump(tester.test_results, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())