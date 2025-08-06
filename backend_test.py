import requests
import sys
import json
import time
from datetime import datetime

class NanoboxDevStackTester:
    def __init__(self, base_url="https://704c959b-d53a-4052-a024-eee63dfa8b78.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_env_id = None
        self.created_service_ids = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if method == 'GET' and 'environments' in endpoint:
                        print(f"   Found {len(response_data)} environments")
                    elif method == 'POST' and 'environments' in endpoint:
                        print(f"   Created environment: {response_data.get('name', 'Unknown')}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response text: {response.text[:200]}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout")
            return False, {}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        return success

    def test_get_environments_empty(self):
        """Test getting environments when none exist"""
        success, response = self.run_test(
            "Get Environments (Empty)",
            "GET",
            "api/environments",
            200
        )
        return success

    def test_create_environment(self):
        """Test creating a new environment"""
        test_env_data = {
            "name": "Test LAMP Stack",
            "stack_type": "LAMP",
            "description": "Test environment for LAMP stack"
        }
        
        success, response = self.run_test(
            "Create Environment",
            "POST",
            "api/environments",
            200,
            data=test_env_data
        )
        
        if success and response:
            self.created_env_id = response.get('id')
            # Store service IDs for later testing
            services = response.get('services', [])
            self.created_service_ids = [service.get('id') for service in services if service.get('id')]
            print(f"   Environment ID: {self.created_env_id}")
            print(f"   Created {len(services)} services: {[s.get('name') for s in services]}")
        
        return success

    def test_get_environments_with_data(self):
        """Test getting environments after creating one"""
        success, response = self.run_test(
            "Get Environments (With Data)",
            "GET",
            "api/environments",
            200
        )
        
        if success and response:
            print(f"   Found environments: {[env.get('name') for env in response]}")
        
        return success

    def test_start_environment(self):
        """Test starting an environment"""
        if not self.created_env_id:
            print("❌ Skipped - No environment ID available")
            return False
            
        success, response = self.run_test(
            "Start Environment",
            "PUT",
            f"api/environments/{self.created_env_id}/start",
            200
        )
        return success

    def test_stop_environment(self):
        """Test stopping an environment"""
        if not self.created_env_id:
            print("❌ Skipped - No environment ID available")
            return False
            
        success, response = self.run_test(
            "Stop Environment",
            "PUT",
            f"api/environments/{self.created_env_id}/stop",
            200
        )
        return success

    def test_toggle_service(self):
        """Test toggling a service"""
        if not self.created_service_ids:
            print("❌ Skipped - No service IDs available")
            return False
            
        service_id = self.created_service_ids[0]
        success, response = self.run_test(
            "Toggle Service",
            "PUT",
            f"api/services/{service_id}/toggle",
            200
        )
        return success

    def test_get_service_logs(self):
        """Test getting service logs"""
        if not self.created_service_ids:
            print("❌ Skipped - No service IDs available")
            return False
            
        service_id = self.created_service_ids[0]
        success, response = self.run_test(
            "Get Service Logs",
            "GET",
            f"api/services/{service_id}/logs",
            200
        )
        
        if success and response:
            print(f"   Found {len(response)} log entries")
        
        return success

    def test_delete_environment(self):
        """Test deleting an environment"""
        if not self.created_env_id:
            print("❌ Skipped - No environment ID available")
            return False
            
        success, response = self.run_test(
            "Delete Environment",
            "DELETE",
            f"api/environments/{self.created_env_id}",
            200
        )
        return success

    def test_create_different_stacks(self):
        """Test creating environments with different stack types"""
        stack_types = ['MEAN', 'Django', 'FastAPI', 'Next.js', 'Vue.js']
        created_ids = []
        
        for stack in stack_types:
            test_env_data = {
                "name": f"Test {stack} Stack",
                "stack_type": stack,
                "description": f"Test environment for {stack} stack"
            }
            
            success, response = self.run_test(
                f"Create {stack} Environment",
                "POST",
                "api/environments",
                200,
                data=test_env_data
            )
            
            if success and response:
                created_ids.append(response.get('id'))
        
        # Clean up created environments
        for env_id in created_ids:
            if env_id:
                self.run_test(
                    f"Cleanup Environment {env_id}",
                    "DELETE",
                    f"api/environments/{env_id}",
                    200
                )
        
        return len(created_ids) == len(stack_types)

def main():
    print("🚀 Starting Nanobox DevStack Manager API Tests")
    print("=" * 60)
    
    # Setup
    tester = NanoboxDevStackTester()
    
    # Run tests in sequence
    tests = [
        tester.test_health_check,
        tester.test_get_environments_empty,
        tester.test_create_environment,
        tester.test_get_environments_with_data,
        tester.test_start_environment,
        tester.test_stop_environment,
        tester.test_toggle_service,
        tester.test_get_service_logs,
        tester.test_create_different_stacks,
        tester.test_delete_environment,
    ]
    
    for test in tests:
        try:
            test()
            time.sleep(0.5)  # Small delay between tests
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())