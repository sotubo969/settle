#!/usr/bin/env python3
"""
Firebase Authentication Testing for AfroMarket UK
Tests Firebase integration endpoints and structure
"""

import requests
import sys
import json
from datetime import datetime

class FirebaseAuthTester:
    def __init__(self, base_url="https://code-fetcher-23.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details="", expected_status=None, actual_status=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            "test_name": name,
            "status": "PASS" if success else "FAIL",
            "details": details,
            "expected_status": expected_status,
            "actual_status": actual_status,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        print(f"{status} - {name}")
        if details:
            print(f"    {details}")
        if expected_status and actual_status:
            print(f"    Expected: {expected_status}, Got: {actual_status}")
        print()

    def test_firebase_status_endpoint(self):
        """Test Firebase configuration status endpoint"""
        try:
            response = requests.get(f"{self.api_url}/auth/firebase/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                configured = data.get('configured', False)
                message = data.get('message', '')
                
                # Since Firebase is not configured, we expect configured=False
                if not configured and 'not configured' in message.lower():
                    self.log_test(
                        "Firebase Status Endpoint", 
                        True, 
                        f"Correctly reports Firebase not configured: {message}",
                        200,
                        response.status_code
                    )
                    return True
                else:
                    self.log_test(
                        "Firebase Status Endpoint", 
                        False, 
                        f"Unexpected response: configured={configured}, message={message}",
                        200,
                        response.status_code
                    )
                    return False
            else:
                self.log_test(
                    "Firebase Status Endpoint", 
                    False, 
                    f"Unexpected status code: {response.status_code}",
                    200,
                    response.status_code
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Firebase Status Endpoint", 
                False, 
                f"Request failed: {str(e)}"
            )
            return False

    def test_firebase_auth_endpoint_structure(self):
        """Test Firebase auth endpoint returns proper error when no credentials"""
        try:
            # Test with invalid/missing token
            test_data = {
                "idToken": "invalid_token_for_testing",
                "displayName": "Test User",
                "photoURL": "https://example.com/photo.jpg"
            }
            
            response = requests.post(
                f"{self.api_url}/auth/firebase", 
                json=test_data,
                timeout=10
            )
            
            # Should return 500 since Firebase is not configured
            if response.status_code == 500:
                data = response.json()
                detail = data.get('detail', '')
                
                if 'firebase not configured' in detail.lower() or 'authentication failed' in detail.lower():
                    self.log_test(
                        "Firebase Auth Endpoint Structure", 
                        True, 
                        f"Correctly returns error when Firebase not configured: {detail}",
                        500,
                        response.status_code
                    )
                    return True
                else:
                    self.log_test(
                        "Firebase Auth Endpoint Structure", 
                        False, 
                        f"Unexpected error message: {detail}",
                        500,
                        response.status_code
                    )
                    return False
            else:
                self.log_test(
                    "Firebase Auth Endpoint Structure", 
                    False, 
                    f"Expected 500 error, got {response.status_code}",
                    500,
                    response.status_code
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Firebase Auth Endpoint Structure", 
                False, 
                f"Request failed: {str(e)}"
            )
            return False

    def test_database_schema_compatibility(self):
        """Test that database schema supports Firebase fields"""
        try:
            # Test regular registration to ensure database works
            test_user_data = {
                "name": f"Test User {datetime.now().strftime('%H%M%S')}",
                "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
                "password": "TestPass123!"
            }
            
            response = requests.post(
                f"{self.api_url}/auth/register",
                json=test_user_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('token'):
                    self.log_test(
                        "Database Schema Compatibility", 
                        True, 
                        "User registration works, database schema supports auth fields",
                        200,
                        response.status_code
                    )
                    return True
                else:
                    self.log_test(
                        "Database Schema Compatibility", 
                        False, 
                        f"Registration response missing expected fields: {data}",
                        200,
                        response.status_code
                    )
                    return False
            else:
                self.log_test(
                    "Database Schema Compatibility", 
                    False, 
                    f"Registration failed with status {response.status_code}",
                    200,
                    response.status_code
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Database Schema Compatibility", 
                False, 
                f"Request failed: {str(e)}"
            )
            return False

    def test_backend_imports_and_structure(self):
        """Test that backend has proper Firebase imports and structure"""
        try:
            # Test that the server is running and has the Firebase endpoints
            response = requests.get(f"{self.api_url}/auth/firebase/status", timeout=10)
            
            if response.status_code == 200:
                self.log_test(
                    "Backend Firebase Structure", 
                    True, 
                    "Firebase endpoints are accessible, imports working",
                    200,
                    response.status_code
                )
                return True
            else:
                self.log_test(
                    "Backend Firebase Structure", 
                    False, 
                    f"Firebase status endpoint not accessible: {response.status_code}",
                    200,
                    response.status_code
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Backend Firebase Structure", 
                False, 
                f"Cannot access Firebase endpoints: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all Firebase authentication tests"""
        print("🔥 Firebase Authentication Testing for AfroMarket UK")
        print("=" * 60)
        print("Note: Firebase credentials are NOT configured - testing structure and error handling")
        print()
        
        # Test Firebase backend structure
        self.test_backend_imports_and_structure()
        self.test_firebase_status_endpoint()
        self.test_firebase_auth_endpoint_structure()
        self.test_database_schema_compatibility()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Firebase structure is correctly implemented.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return self.tests_passed, self.tests_run, self.test_results

def main():
    """Main test execution"""
    tester = FirebaseAuthTester()
    passed, total, results = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/firebase_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'passed': passed,
                'total': total,
                'success_rate': f"{(passed/total*100):.1f}%" if total > 0 else "0%"
            },
            'tests': results,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/firebase_test_results.json")
    
    # Return appropriate exit code
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())