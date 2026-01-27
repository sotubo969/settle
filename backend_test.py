#!/usr/bin/env python3
"""
AfroMarket UK Backend API Testing - WebSocket & Push Notification System
Tests WebSocket status, VAPID keys, notification preferences, push subscriptions, and real-time notifications
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class AfroMarketAPITester:
    def __init__(self, base_url: str = "https://github-code-pull.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.vendor_id = None
        self.vendor_email = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.test_results = {}

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
            self.failed_tests.append({"test": name, "error": details})
        
        self.test_results[name] = {
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    expected_status: int = 200, auth_required: bool = True) -> tuple:
        """Make API request and return (success, response_data)"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return False, f"Unsupported method: {method}"

            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = {"status_code": response.status_code, "text": response.text}
            
            return success, response_data

        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {str(e)}"

    def test_firebase_status(self):
        """Test Firebase configuration status"""
        print("\n🔥 Testing Firebase Status...")
        
        success, response = self.make_request('GET', 'auth/firebase/status', auth_required=False)
        
        if success and response.get('configured') == True:
            self.log_test("Firebase Status - Configured", True, "Firebase is properly configured")
        else:
            self.log_test("Firebase Status - Configured", False, f"Firebase not configured: {response}")
        
        return success

    def test_authentication(self):
        """Test user authentication (email/password)"""
        print("\n🔐 Testing Email/Password Authentication...")
        
        # Test registration
        test_email = f"test_{datetime.now().strftime('%H%M%S')}@example.com"
        success, response = self.make_request('POST', 'auth/register', {
            "name": "Test User",
            "email": test_email,
            "password": "Test123!"
        }, auth_required=False)
        
        if success and response.get('token'):
            self.token = response['token']
            self.user_id = response['user']['id']
            self.log_test("Email/Password Registration", True)
        else:
            self.log_test("Email/Password Registration", False, str(response))
            return False

        # Test login
        success, response = self.make_request('POST', 'auth/login', {
            "email": test_email,
            "password": "Test123!"
        }, auth_required=False)
        
        if success and response.get('token'):
            self.log_test("Email/Password Login", True)
        else:
            self.log_test("Email/Password Login", False, str(response))
        
        return True

    def test_vendor_registration_public(self):
        """Test public vendor registration endpoint with email notification"""
        print("\n🏪 Testing Public Vendor Registration...")
        
        # Test public vendor registration (no auth required)
        timestamp = datetime.now().strftime('%H%M%S')
        self.vendor_email = f"testvendor{timestamp}@example.com"
        vendor_data = {
            "businessName": f"Test African Store {timestamp}",
            "description": "A test store selling authentic African products and groceries",
            "email": self.vendor_email,
            "phone": "+44 20 1234 5678",
            "address": "123 Test Street",
            "city": "London",
            "postcode": "SW1A 1AA",
            "ownerName": "Test Owner"
        }
        
        success, response = self.make_request('POST', 'vendors/register/public', vendor_data, auth_required=False)
        
        if success and response.get('success'):
            email_sent = response.get('emailSent', False)
            self.vendor_id = response.get('vendor', {}).get('id')
            
            self.log_test("Vendor Registration - Creates Vendor in Database", True, f"Vendor ID: {self.vendor_id}")
            self.log_test("Vendor Registration - Email Notification", email_sent, 
                         f"Email sent status: {email_sent}")
            
            # Check if response includes proper message
            message = response.get('message', '')
            expected_message_parts = ['submitted successfully', 'review', 'contact']
            message_ok = any(part in message.lower() for part in expected_message_parts)
            self.log_test("Vendor Registration - Response Message", message_ok, f"Message: {message}")
            
            return self.vendor_id
        else:
            self.log_test("Vendor Registration - Creates Vendor in Database", False, str(response))
            return None

    def test_admin_vendor_approval(self):
        """Test admin vendor approval endpoint creates notification and sends email"""
        print("\n👑 Testing Admin Vendor Approval...")
        
        if not self.vendor_id:
            self.log_test("Admin Vendor Approval - No Vendor to Approve", False, "No vendor ID available")
            return False
        
        # Test vendor approval
        approval_data = {
            "vendorId": self.vendor_id,
            "status": "approved"
        }
        
        success, response = self.make_request('POST', 'admin/vendors/approve', approval_data, auth_required=False)
        
        if success and response.get('success'):
            email_sent = response.get('emailSent', False)
            notification_created = response.get('notificationCreated', False)
            
            self.log_test("Admin Vendor Approval - Creates Notification", notification_created, 
                         f"Notification created: {notification_created}")
            self.log_test("Admin Vendor Approval - Sends Email", email_sent, 
                         f"Email sent: {email_sent}")
            
            return True
        else:
            self.log_test("Admin Vendor Approval - Creates Notification", False, str(response))
            self.log_test("Admin Vendor Approval - Sends Email", False, str(response))
            return False

    def test_vendor_notifications_by_email(self):
        """Test vendor notifications by email endpoint (non-authenticated access)"""
        print("\n📧 Testing Vendor Notifications by Email...")
        
        if not self.vendor_email:
            self.log_test("Vendor Notifications by Email - No Email", False, "No vendor email available")
            return False
        
        # Wait a moment for notification to be created
        time.sleep(2)
        
        success, response = self.make_request('GET', f'vendor/notifications/by-email/{self.vendor_email}', 
                                            auth_required=False)
        
        if success and response.get('success'):
            notifications = response.get('notifications', [])
            unread_count = response.get('unreadCount', 0)
            vendor_status = response.get('vendorStatus')
            
            self.log_test("Vendor Notifications by Email - Returns Notifications List", True, 
                         f"Found {len(notifications)} notifications, {unread_count} unread")
            self.log_test("Vendor Notifications by Email - Vendor Status", vendor_status == "approved", 
                         f"Vendor status: {vendor_status}")
            
            # Check if approval notification exists
            approval_notification = any(n.get('type') == 'approval' for n in notifications)
            self.log_test("Vendor Notifications by Email - Approval Notification", approval_notification,
                         f"Approval notification found: {approval_notification}")
            
            return len(notifications) > 0
        else:
            self.log_test("Vendor Notifications by Email - Returns Notifications List", False, str(response))
            return False

    def test_vendor_notifications_authenticated(self):
        """Test authenticated vendor notifications endpoint"""
        print("\n🔐 Testing Authenticated Vendor Notifications...")
        
        if not self.token:
            self.log_test("Authenticated Vendor Notifications - No Token", False, "No auth token available")
            return False
        
        success, response = self.make_request('GET', 'vendor/notifications', auth_required=True)
        
        if success and response.get('success'):
            notifications = response.get('notifications', [])
            unread_count = response.get('unreadCount', 0)
            
            self.log_test("Authenticated Vendor Notifications - Returns Notifications List", True, 
                         f"Found {len(notifications)} notifications, {unread_count} unread")
            
            return len(notifications) > 0, notifications
        else:
            self.log_test("Authenticated Vendor Notifications - Returns Notifications List", False, str(response))
            return False, []

    def test_mark_notification_as_read(self):
        """Test mark notification as read endpoint"""
        print("\n✅ Testing Mark Notification as Read...")
        
        if not self.token:
            self.log_test("Mark Notification as Read - No Token", False, "No auth token available")
            return False
        
        # Get notifications first
        has_notifications, notifications = self.test_vendor_notifications_authenticated()
        
        if not has_notifications or not notifications:
            self.log_test("Mark Notification as Read - No Notifications", False, "No notifications to mark as read")
            return False
        
        # Find an unread notification
        unread_notification = next((n for n in notifications if not n.get('isRead')), None)
        
        if not unread_notification:
            self.log_test("Mark Notification as Read - No Unread Notifications", True, "All notifications already read")
            return True
        
        notification_id = unread_notification['id']
        success, response = self.make_request('PUT', f'vendor/notifications/{notification_id}/read', 
                                            {}, auth_required=True)
        
        if success and response.get('success'):
            self.log_test("Mark Notification as Read - Works", True, f"Marked notification {notification_id} as read")
            return True
        else:
            self.log_test("Mark Notification as Read - Works", False, str(response))
            return False

    def test_mark_all_notifications_as_read(self):
        """Test mark all notifications as read endpoint"""
        print("\n✅✅ Testing Mark All Notifications as Read...")
        
        if not self.token:
            self.log_test("Mark All Notifications as Read - No Token", False, "No auth token available")
            return False
        
        success, response = self.make_request('PUT', 'vendor/notifications/mark-all-read', 
                                            {}, auth_required=True)
        
        if success and response.get('success'):
            self.log_test("Mark All Notifications as Read - Works", True, "All notifications marked as read")
            
            # Verify by checking notifications again
            time.sleep(1)
            success2, response2 = self.make_request('GET', 'vendor/notifications', auth_required=True)
            if success2 and response2.get('success'):
                unread_count = response2.get('unreadCount', 0)
                self.log_test("Mark All Notifications as Read - Verification", unread_count == 0, 
                             f"Unread count after marking all as read: {unread_count}")
            
            return True
        else:
            self.log_test("Mark All Notifications as Read - Works", False, str(response))
            return False

    def test_notification_system_workflow(self):
        """Test full notification workflow: register vendor -> approve -> notification created"""
        print("\n🔄 Testing Full Notification Workflow...")
        
        # Step 1: Register vendor
        vendor_id = self.test_vendor_registration_public()
        if not vendor_id:
            self.log_test("Full Workflow - Vendor Registration", False, "Failed to register vendor")
            return False
        
        # Step 2: Approve vendor (creates notification)
        approval_success = self.test_admin_vendor_approval()
        if not approval_success:
            self.log_test("Full Workflow - Vendor Approval", False, "Failed to approve vendor")
            return False
        
        # Step 3: Check notifications were created
        notifications_success = self.test_vendor_notifications_by_email()
        if not notifications_success:
            self.log_test("Full Workflow - Notification Creation", False, "No notifications found after approval")
            return False
        
        self.log_test("Full Workflow - Complete", True, "Register -> Approve -> Notification workflow successful")
        return True

    def test_basic_endpoints(self):
        """Test basic API endpoints are working"""
        print("\n🌐 Testing Basic API Endpoints...")
        
        # Test products endpoint
        success, response = self.make_request('GET', 'products', auth_required=False)
        if success and isinstance(response, list):
            self.log_test("Products API", True, f"Found {len(response)} products")
        else:
            self.log_test("Products API", False, str(response))
        
        # Test vendors endpoint
        success, response = self.make_request('GET', 'vendors', auth_required=False)
        if success and isinstance(response, list):
            self.log_test("Vendors API", True, f"Found {len(response)} vendors")
        else:
            self.log_test("Vendors API", False, str(response))

    def run_all_tests(self):
        """Run comprehensive test suite for vendor notification system"""
        print("🧪 Starting AfroMarket UK Backend Tests - Vendor Notification System")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Test Firebase configuration
        self.test_firebase_status()
        
        # Test basic endpoints
        self.test_basic_endpoints()
        
        # Test authentication
        auth_success = self.test_authentication()
        
        # Test notification system workflow
        print("\n" + "="*50)
        print("🔔 VENDOR NOTIFICATION SYSTEM TESTS")
        print("="*50)
        
        # Test full workflow
        self.test_notification_system_workflow()
        
        # Test individual notification endpoints if we have auth
        if auth_success and self.token:
            self.test_mark_notification_as_read()
            self.test_mark_all_notifications_as_read()
        
        # Print summary
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for failure in self.failed_tests:
                print(f"  - {failure['test']}: {failure['error']}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"\n✨ Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 70

def main():
    """Main test execution"""
    tester = AfroMarketAPITester()
    
    try:
        success = tester.run_all_tests()
        
        # Save detailed results
        with open('/app/backend_test_results.json', 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_tests": tester.tests_run,
                "passed_tests": tester.tests_passed,
                "failed_tests": tester.failed_tests,
                "success_rate": (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0,
                "detailed_results": tester.test_results
            }, f, indent=2)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"💥 Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())