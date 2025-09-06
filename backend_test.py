import requests
import sys
import json
from datetime import datetime

class MedicineQualityAPITester:
    def __init__(self, base_url="https://medverify-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {json.dumps(response_data, indent=2)}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    return success, response_data
                except:
                    return success, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )

    def test_verify_valid_medicine(self):
        """Test verification with a valid batch code"""
        # First get some logs to find valid batch codes
        success, logs_data = self.run_test(
            "Get Logs for Sample Batch Codes",
            "GET", 
            "logs?limit=5",
            200
        )
        
        if success and logs_data and len(logs_data) > 0:
            # Use an existing batch code from logs
            sample_batch = logs_data[0].get('batch_code', 'MED123456A')
            print(f"   Using existing batch code: {sample_batch}")
        else:
            # Use a test batch code
            sample_batch = 'MED123456A'
            print(f"   Using test batch code: {sample_batch}")
        
        return self.run_test(
            "Verify Medicine - Valid Code",
            "POST",
            "verify",
            200,
            data={
                "code": sample_batch,
                "lat": 40.7128,
                "lng": -74.0060
            }
        )

    def test_verify_invalid_medicine(self):
        """Test verification with an invalid batch code"""
        return self.run_test(
            "Verify Medicine - Invalid Code",
            "POST",
            "verify", 
            200,
            data={
                "code": "INVALID999999Z",
                "lat": 40.7128,
                "lng": -74.0060
            }
        )

    def test_verify_without_location(self):
        """Test verification without location data"""
        return self.run_test(
            "Verify Medicine - No Location",
            "POST",
            "verify",
            200,
            data={"code": "TEST123456B"}
        )

    def test_admin_login_valid(self):
        """Test admin login with valid credentials"""
        success, response = self.run_test(
            "Admin Login - Valid Credentials",
            "POST",
            "admin/login",
            200,
            data={
                "username": "admin",
                "password": "admin123"
            }
        )
        
        if success and response.get('success') and response.get('token'):
            self.token = response['token']
            print(f"   Token received: {self.token[:20]}...")
            return True, response
        return False, response

    def test_admin_login_invalid(self):
        """Test admin login with invalid credentials"""
        return self.run_test(
            "Admin Login - Invalid Credentials",
            "POST",
            "admin/login",
            200,
            data={
                "username": "wrong",
                "password": "wrong"
            }
        )

    def test_get_logs(self):
        """Test getting verification logs"""
        return self.run_test(
            "Get Verification Logs",
            "GET",
            "logs",
            200
        )

    def test_get_logs_with_limit(self):
        """Test getting logs with limit parameter"""
        return self.run_test(
            "Get Logs with Limit",
            "GET",
            "logs?limit=5",
            200
        )

    def test_get_stats(self):
        """Test getting statistics"""
        return self.run_test(
            "Get Statistics",
            "GET",
            "stats",
            200
        )

    def test_verify_edge_cases(self):
        """Test verification with edge cases"""
        edge_cases = [
            ("Empty Code", {"code": ""}),
            ("Whitespace Code", {"code": "   "}),
            ("Very Long Code", {"code": "A" * 100}),
            ("Special Characters", {"code": "MED@#$%^&*()"}),
        ]
        
        results = []
        for case_name, data in edge_cases:
            success, response = self.run_test(
                f"Verify Medicine - {case_name}",
                "POST",
                "verify",
                200,  # API should handle gracefully
                data=data
            )
            results.append((case_name, success))
        
        return all(result[1] for result in results), results

def main():
    """Main test execution"""
    print("🧪 Starting Medicine Quality Monitor API Tests")
    print("=" * 60)
    
    tester = MedicineQualityAPITester()
    
    # Test sequence
    test_results = []
    
    # Basic API tests
    print("\n📡 BASIC API TESTS")
    print("-" * 30)
    success, _ = tester.test_root_endpoint()
    test_results.append(("Root Endpoint", success))
    
    # Medicine verification tests
    print("\n💊 MEDICINE VERIFICATION TESTS")
    print("-" * 30)
    success, _ = tester.test_verify_valid_medicine()
    test_results.append(("Verify Valid Medicine", success))
    
    success, _ = tester.test_verify_invalid_medicine()
    test_results.append(("Verify Invalid Medicine", success))
    
    success, _ = tester.test_verify_without_location()
    test_results.append(("Verify Without Location", success))
    
    success, _ = tester.test_verify_edge_cases()
    test_results.append(("Verify Edge Cases", success))
    
    # Admin authentication tests
    print("\n🔐 ADMIN AUTHENTICATION TESTS")
    print("-" * 30)
    success, _ = tester.test_admin_login_valid()
    test_results.append(("Admin Login Valid", success))
    
    success, _ = tester.test_admin_login_invalid()
    test_results.append(("Admin Login Invalid", success))
    
    # Data retrieval tests
    print("\n📊 DATA RETRIEVAL TESTS")
    print("-" * 30)
    success, _ = tester.test_get_logs()
    test_results.append(("Get Logs", success))
    
    success, _ = tester.test_get_logs_with_limit()
    test_results.append(("Get Logs with Limit", success))
    
    success, _ = tester.test_get_stats()
    test_results.append(("Get Statistics", success))
    
    # Print final results
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Overall Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the API implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())