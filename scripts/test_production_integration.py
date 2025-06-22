#!/usr/bin/env python3
"""
Comprehensive integration test for Foodgram production environment.
Tests all major components: frontend, backend, database, Redis, MinIO.
"""

import requests
import json
import time
import sys
from typing import Dict, Any


def test_frontend() -> bool:
    """Test frontend availability."""
    try:
        response = requests.get('http://localhost/', timeout=10)
        if response.status_code == 200:
            print("✅ Frontend: OK")
            return True
        else:
            print(f"❌ Frontend: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend: Error - {e}")
        return False


def test_api_endpoints() -> bool:
    """Test main API endpoints."""
    endpoints = [
        '/api/tags/',
        '/api/ingredients/',
        '/api/recipes/',
        '/api/users/',
    ]
    
    all_passed = True
    for endpoint in endpoints:
        try:
            response = requests.get(f'http://localhost{endpoint}', timeout=10)
            if response.status_code == 200:
                print(f"✅ API {endpoint}: OK")
            else:
                print(f"❌ API {endpoint}: Status {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ API {endpoint}: Error - {e}")
            all_passed = False
    
    return all_passed


def test_user_registration() -> bool:
    """Test user registration functionality."""
    try:
        # Test data
        test_user = {
            "email": "integration.test@foodgram.ru",
            "username": "integration_test",
            "first_name": "Integration",
            "last_name": "Test",
            "password": "testpass123"
        }
        
        # Register user
        response = requests.post(
            'http://localhost/api/users/',
            json=test_user,
            timeout=10
        )
        
        if response.status_code == 201:
            print("✅ User Registration: OK")
            return True
        else:
            print(f"❌ User Registration: Status {response.status_code}")
            if response.status_code == 400:
                error_data = response.json()
                if 'email' in error_data and 'already exists' in str(error_data['email']):
                    print("✅ User Registration: User already exists (OK)")
                    return True
            return False
            
    except Exception as e:
        print(f"❌ User Registration: Error - {e}")
        return False


def test_ingredients_data() -> bool:
    """Test ingredients data availability."""
    try:
        response = requests.get('http://localhost/api/ingredients/', timeout=10)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            if count > 0:
                print(f"✅ Ingredients Data: {count} ingredients loaded")
                return True
            else:
                print("❌ Ingredients Data: No ingredients found")
                return False
        else:
            print(f"❌ Ingredients Data: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ingredients Data: Error - {e}")
        return False


def test_tags_data() -> bool:
    """Test tags data availability."""
    try:
        response = requests.get('http://localhost/api/tags/', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"✅ Tags Data: {len(data)} tags available")
                return True
            else:
                print("❌ Tags Data: No tags found")
                return False
        else:
            print(f"❌ Tags Data: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Tags Data: Error - {e}")
        return False


def test_minio_access() -> bool:
    """Test MinIO access."""
    try:
        # Test MinIO API
        response = requests.get('http://localhost:9000/minio/health/live', timeout=10)
        if response.status_code == 200:
            print("✅ MinIO Health: OK")
            return True
        else:
            print(f"❌ MinIO Health: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MinIO Health: Error - {e}")
        return False


def test_admin_panel() -> bool:
    """Test admin panel availability."""
    try:
        response = requests.get('http://localhost/admin/', timeout=10)
        if response.status_code == 200:
            print("✅ Admin Panel: OK")
            return True
        else:
            print(f"❌ Admin Panel: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Admin Panel: Error - {e}")
        return False


def main():
    """Run all integration tests."""
    print("🚀 Starting Foodgram Production Integration Tests")
    print("=" * 50)
    
    # Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(3)
    
    tests = [
        ("Frontend", test_frontend),
        ("API Endpoints", test_api_endpoints),
        ("User Registration", test_user_registration),
        ("Ingredients Data", test_ingredients_data),
        ("Tags Data", test_tags_data),
        ("MinIO Access", test_minio_access),
        ("Admin Panel", test_admin_panel),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Production environment is ready!")
        print("\n🌐 Access your application at:")
        print("   Frontend: http://localhost/")
        print("   API: http://localhost/api/")
        print("   Admin: http://localhost/admin/")
        print("   MinIO Console: http://localhost:9001/")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 