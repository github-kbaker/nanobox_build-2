#!/usr/bin/env python3
"""
Backend Test Suite for Nanobox DevStack API
Tests all the Nanobox DevStack API endpoints
"""

import requests
import json
import sys
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from frontend .env
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://api-connector-8.preview.emergentagent.com')
BASE_URL = f"{BACKEND_URL}/api"

print(f"Testing Nanobox DevStack API at: {BASE_URL}")
print("=" * 60)

def test_health_endpoint():
    """Test /api/nanobox/health endpoint"""
    print("\n1. Testing /api/nanobox/health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/nanobox/health", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2, default=str)}")
            
            # Validate expected fields
            expected_fields = ['status', 'service', 'version', 'timestamp']
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                print(f"   ❌ FAIL: Missing fields: {missing_fields}")
                return False
            
            if data.get('status') == 'healthy' and data.get('service') == 'nanobox-devstack':
                print("   ✅ PASS: Health check returned expected data")
                return True
            else:
                print(f"   ❌ FAIL: Unexpected status or service name")
                return False
        else:
            print(f"   ❌ FAIL: Expected 200, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ FAIL: Exception occurred: {str(e)}")
        return False

def test_status_endpoint():
    """Test /api/nanobox/status endpoint"""
    print("\n2. Testing /api/nanobox/status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/nanobox/status", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2, default=str)}")
            
            # Validate expected fields
            expected_fields = ['status', 'uptime', 'cpu_usage', 'memory_usage', 'disk_usage', 'timestamp']
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                print(f"   ❌ FAIL: Missing fields: {missing_fields}")
                return False
            
            # Validate data types
            if (isinstance(data.get('cpu_usage'), (int, float)) and 
                isinstance(data.get('memory_usage'), (int, float)) and 
                isinstance(data.get('disk_usage'), (int, float))):
                print("   ✅ PASS: System status returned with proper metrics")
                return True
            else:
                print(f"   ❌ FAIL: Invalid data types for usage metrics")
                return False
        else:
            print(f"   ❌ FAIL: Expected 200, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ FAIL: Exception occurred: {str(e)}")
        return False

def test_metrics_endpoint():
    """Test /api/nanobox/metrics endpoint"""
    print("\n3. Testing /api/nanobox/metrics endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/nanobox/metrics", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2, default=str)}")
            
            # Validate expected fields
            expected_fields = ['cpu_usage', 'cpu_count', 'memory_total', 'memory_available', 
                             'memory_usage', 'disk_total', 'disk_free', 'disk_usage', 
                             'network_sent', 'network_recv', 'timestamp']
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                print(f"   ❌ FAIL: Missing fields: {missing_fields}")
                return False
            
            # Validate numeric fields
            numeric_fields = ['cpu_usage', 'cpu_count', 'memory_total', 'memory_available', 
                            'memory_usage', 'disk_total', 'disk_free', 'disk_usage', 
                            'network_sent', 'network_recv']
            
            for field in numeric_fields:
                if not isinstance(data.get(field), (int, float)):
                    print(f"   ❌ FAIL: Field {field} is not numeric")
                    return False
            
            print("   ✅ PASS: Detailed metrics returned with all expected fields")
            return True
        else:
            print(f"   ❌ FAIL: Expected 200, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ FAIL: Exception occurred: {str(e)}")
        return False

def test_containers_endpoint():
    """Test /api/nanobox/containers endpoint"""
    print("\n4. Testing /api/nanobox/containers endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/nanobox/containers", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2, default=str)}")
            
            if not isinstance(data, list):
                print(f"   ❌ FAIL: Expected list, got {type(data)}")
                return False
            
            if len(data) == 0:
                print(f"   ❌ FAIL: No containers returned")
                return False
            
            # Validate container structure
            expected_fields = ['id', 'name', 'status', 'image', 'created', 'ports', 'cpu_usage', 'memory_usage']
            for container in data:
                missing_fields = [field for field in expected_fields if field not in container]
                if missing_fields:
                    print(f"   ❌ FAIL: Container missing fields: {missing_fields}")
                    return False
            
            # Check if nanobox-web-001 exists (needed for container management tests)
            container_ids = [c['id'] for c in data]
            if 'nanobox-web-001' not in container_ids:
                print(f"   ❌ FAIL: Required container 'nanobox-web-001' not found")
                return False
            
            print(f"   ✅ PASS: {len(data)} containers returned with proper structure")
            return True
        else:
            print(f"   ❌ FAIL: Expected 200, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ FAIL: Exception occurred: {str(e)}")
        return False

def test_container_start(container_id="nanobox-web-001"):
    """Test /api/nanobox/containers/{container_id}/start endpoint"""
    print(f"\n5. Testing /api/nanobox/containers/{container_id}/start endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/nanobox/containers/{container_id}/start", timeout=15)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2, default=str)}")
            
            # Validate expected fields
            expected_fields = ['message', 'status', 'timestamp']
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                print(f"   ❌ FAIL: Missing fields: {missing_fields}")
                return False
            
            if container_id in data.get('message', '') and data.get('status') == 'running':
                print("   ✅ PASS: Container start operation successful")
                return True
            else:
                print(f"   ❌ FAIL: Unexpected response content")
                return False
        else:
            print(f"   ❌ FAIL: Expected 200, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ FAIL: Exception occurred: {str(e)}")
        return False

def test_container_stop(container_id="nanobox-web-001"):
    """Test /api/nanobox/containers/{container_id}/stop endpoint"""
    print(f"\n6. Testing /api/nanobox/containers/{container_id}/stop endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/nanobox/containers/{container_id}/stop", timeout=15)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2, default=str)}")
            
            # Validate expected fields
            expected_fields = ['message', 'status', 'timestamp']
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                print(f"   ❌ FAIL: Missing fields: {missing_fields}")
                return False
            
            if container_id in data.get('message', '') and data.get('status') == 'stopped':
                print("   ✅ PASS: Container stop operation successful")
                return True
            else:
                print(f"   ❌ FAIL: Unexpected response content")
                return False
        else:
            print(f"   ❌ FAIL: Expected 200, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ FAIL: Exception occurred: {str(e)}")
        return False

def test_container_restart(container_id="nanobox-web-001"):
    """Test /api/nanobox/containers/{container_id}/restart endpoint"""
    print(f"\n7. Testing /api/nanobox/containers/{container_id}/restart endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/nanobox/containers/{container_id}/restart", timeout=15)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2, default=str)}")
            
            # Validate expected fields
            expected_fields = ['message', 'status', 'timestamp']
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                print(f"   ❌ FAIL: Missing fields: {missing_fields}")
                return False
            
            if container_id in data.get('message', '') and data.get('status') == 'running':
                print("   ✅ PASS: Container restart operation successful")
                return True
            else:
                print(f"   ❌ FAIL: Unexpected response content")
                return False
        else:
            print(f"   ❌ FAIL: Expected 200, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ FAIL: Exception occurred: {str(e)}")
        return False

def main():
    """Run all tests"""
    print(f"Starting Nanobox DevStack API Tests at {datetime.now()}")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)
    
    tests = [
        test_health_endpoint,
        test_status_endpoint,
        test_metrics_endpoint,
        test_containers_endpoint,
        test_container_start,
        test_container_stop,
        test_container_restart
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ FAIL: Test failed with exception: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "Health Check",
        "System Status", 
        "Resource Metrics",
        "Container List",
        "Container Start",
        "Container Stop", 
        "Container Restart"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Nanobox DevStack API tests PASSED!")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)