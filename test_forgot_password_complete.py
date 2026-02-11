#!/usr/bin/env python3
"""
Complete Forgot Password Flow Testing for AfroMarket UK
Tests the full forgot password functionality including token verification and password reset.
"""

import requests
import json
import sqlite3
from datetime import datetime

# Configuration
BASE_URL = "https://afromarket-staging.preview.emergentagent.com/api"
OWNER_EMAIL = "sotubodammy@gmail.com"

class ForgotPasswordTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def make_request(self, method: str, endpoint: str, data: dict = None, headers: dict = None) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{BASE_URL}{endpoint}"
        
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=default_headers, params=data)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=default_headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except Exception as e:
            print(f"Request failed: {str(e)}")
            raise
    
    def get_valid_reset_token(self):
        """Get a valid reset token from the database"""
        try:
            conn = sqlite3.connect('backend/afromarket.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT token FROM password_reset_tokens 
                WHERE used = 0 AND expires_at > datetime('now')
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            else:
                return None
                
        except Exception as e:
            print(f"Database error: {str(e)}")
            return None
    
    def test_complete_forgot_password_flow(self):
        """Test the complete forgot password flow"""
        print("=" * 80)
        print("COMPLETE FORGOT PASSWORD FLOW TESTING")
        print("=" * 80)
        
        # Step 1: Request password reset
        print("\n🔑 Step 1: Request Password Reset")
        print("-" * 40)
        
        try:
            forgot_data = {"email": OWNER_EMAIL}
            response = self.make_request("POST", "/auth/forgot-password", forgot_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Request Password Reset", True, 
                                f"Password reset requested for {OWNER_EMAIL}")
                else:
                    self.log_test("Request Password Reset", False, f"Unexpected response: {data}")
                    return
            else:
                self.log_test("Request Password Reset", False, f"HTTP {response.status_code}: {response.text}")
                return
        except Exception as e:
            self.log_test("Request Password Reset", False, f"Exception: {str(e)}")
            return
        
        # Step 2: Get valid token from database
        print("\n🔑 Step 2: Get Reset Token")
        print("-" * 40)
        
        reset_token = self.get_valid_reset_token()
        if reset_token:
            self.log_test("Get Reset Token", True, f"Retrieved valid token: {reset_token[:20]}...")
        else:
            self.log_test("Get Reset Token", False, "No valid reset token found in database")
            return
        
        # Step 3: Verify reset token
        print("\n🔑 Step 3: Verify Reset Token")
        print("-" * 40)
        
        try:
            response = self.make_request("GET", f"/auth/reset-password/verify/{reset_token}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid") and data.get("email") == OWNER_EMAIL:
                    self.log_test("Verify Reset Token", True, 
                                f"Token verified successfully for {data.get('email')}")
                    expires_at = data.get("expiresAt")
                    if expires_at:
                        print(f"   Token expires at: {expires_at}")
                else:
                    self.log_test("Verify Reset Token", False, f"Invalid token response: {data}")
                    return
            else:
                self.log_test("Verify Reset Token", False, f"HTTP {response.status_code}: {response.text}")
                return
        except Exception as e:
            self.log_test("Verify Reset Token", False, f"Exception: {str(e)}")
            return
        
        # Step 4: Test password validation rules
        print("\n🔑 Step 4: Test Password Validation")
        print("-" * 40)
        
        validation_tests = [
            {
                "name": "Valid Password",
                "password": "NewPassword123!",
                "confirmPassword": "NewPassword123!",
                "should_pass": True
            },
            {
                "name": "Password Too Short",
                "password": "Short1!",
                "confirmPassword": "Short1!",
                "should_pass": False,
                "expected_error": "at least 8 characters"
            },
            {
                "name": "No Uppercase Letter",
                "password": "lowercase123!",
                "confirmPassword": "lowercase123!",
                "should_pass": False,
                "expected_error": "uppercase letter"
            },
            {
                "name": "No Lowercase Letter",
                "password": "UPPERCASE123!",
                "confirmPassword": "UPPERCASE123!",
                "should_pass": False,
                "expected_error": "lowercase letter"
            },
            {
                "name": "No Number",
                "password": "NoNumbers!",
                "confirmPassword": "NoNumbers!",
                "should_pass": False,
                "expected_error": "number"
            },
            {
                "name": "Passwords Don't Match",
                "password": "ValidPassword123!",
                "confirmPassword": "DifferentPassword123!",
                "should_pass": False,
                "expected_error": "do not match"
            }
        ]
        
        # Test all validation rules except the valid one (save that for last)
        for test_case in validation_tests[1:]:  # Skip the valid password test
            try:
                reset_data = {
                    "token": reset_token,
                    "password": test_case["password"],
                    "confirmPassword": test_case["confirmPassword"]
                }
                
                response = self.make_request("POST", "/auth/reset-password", reset_data)
                
                if test_case["should_pass"]:
                    if response.status_code == 200:
                        self.log_test(f"Password Validation - {test_case['name']}", True, "Password accepted")
                    else:
                        self.log_test(f"Password Validation - {test_case['name']}", False, 
                                    f"Expected success, got HTTP {response.status_code}: {response.text}")
                else:
                    if response.status_code == 400:
                        data = response.json()
                        error_detail = data.get("detail", "").lower()
                        if test_case["expected_error"].lower() in error_detail:
                            self.log_test(f"Password Validation - {test_case['name']}", True, 
                                        f"Correctly rejected: {test_case['expected_error']}")
                        else:
                            self.log_test(f"Password Validation - {test_case['name']}", False, 
                                        f"Expected '{test_case['expected_error']}', got: {data.get('detail')}")
                    else:
                        self.log_test(f"Password Validation - {test_case['name']}", False, 
                                    f"Expected 400 error, got HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Password Validation - {test_case['name']}", False, f"Exception: {str(e)}")
        
        # Step 5: Reset password with valid data
        print("\n🔑 Step 5: Reset Password")
        print("-" * 40)
        
        new_password = "NewPassword123!"
        
        try:
            reset_data = {
                "token": reset_token,
                "password": new_password,
                "confirmPassword": new_password
            }
            
            response = self.make_request("POST", "/auth/reset-password", reset_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Reset Password", True, 
                                f"Password reset successfully: {data.get('message')}")
                else:
                    self.log_test("Reset Password", False, f"Reset failed: {data}")
                    return
            else:
                self.log_test("Reset Password", False, f"HTTP {response.status_code}: {response.text}")
                return
        except Exception as e:
            self.log_test("Reset Password", False, f"Exception: {str(e)}")
            return
        
        # Step 6: Verify token is invalidated after use
        print("\n🔑 Step 6: Verify Token Invalidation")
        print("-" * 40)
        
        try:
            response = self.make_request("GET", f"/auth/reset-password/verify/{reset_token}")
            
            if response.status_code == 400:
                data = response.json()
                if "invalid" in data.get("detail", "").lower() or "expired" in data.get("detail", "").lower():
                    self.log_test("Token Invalidation", True, 
                                "Token properly invalidated after use")
                else:
                    self.log_test("Token Invalidation", False, f"Unexpected error: {data}")
            else:
                self.log_test("Token Invalidation", False, 
                            f"Expected 400 error, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Token Invalidation", False, f"Exception: {str(e)}")
        
        # Step 7: Test login with new password
        print("\n🔑 Step 7: Test Login with New Password")
        print("-" * 40)
        
        try:
            login_data = {
                "email": OWNER_EMAIL,
                "password": new_password
            }
            
            response = self.make_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    user_data = data.get("user", {})
                    self.log_test("Login with New Password", True, 
                                f"Login successful with new password - User: {user_data.get('name')} ({user_data.get('email')})")
                else:
                    self.log_test("Login with New Password", False, f"Login failed: {data}")
            else:
                self.log_test("Login with New Password", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Login with New Password", False, f"Exception: {str(e)}")
        
        # Step 8: Verify old password no longer works
        print("\n🔑 Step 8: Verify Old Password Rejected")
        print("-" * 40)
        
        try:
            login_data = {
                "email": OWNER_EMAIL,
                "password": "owner2025!"  # Old password
            }
            
            response = self.make_request("POST", "/auth/login", login_data)
            
            if response.status_code == 401:
                self.log_test("Old Password Rejected", True, 
                            "Old password correctly rejected after reset")
            elif response.status_code == 200:
                self.log_test("Old Password Rejected", False, 
                            "Old password still works - password reset may have failed")
            else:
                self.log_test("Old Password Rejected", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Old Password Rejected", False, f"Exception: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("FORGOT PASSWORD FLOW TEST SUMMARY")
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
    tester = ForgotPasswordTester()
    tester.test_complete_forgot_password_flow()
    tester.print_summary()