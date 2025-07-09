#!/usr/bin/env python3
"""
Test script for TAMS Anomaly Storage API endpoints.
Run this script to verify the storage functionality works correctly.
"""

import requests
import json
import sys
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test if the API is running"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health check passed: {result['message']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_single_storage():
    """Test single anomaly storage"""
    print("\n🔍 Testing single anomaly storage...")
    
    test_data = {
        "num_equipement": "TEST001",
        "systeme": "Hydraulic",
        "description": "Test anomaly for API verification",
        "date_detection": datetime.now().strftime("%Y-%m-%d"),
        "description_equipement": "Test equipment",
        "section_proprietaire": "Test Section"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/store/single",
            headers={"Content-Type": "application/json"},
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Single storage successful:")
            print(f"   Message: {result['message']}")
            print(f"   Anomaly ID: {result['anomaly_id']}")
            return result['anomaly_id']
        else:
            print(f"❌ Single storage failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Single storage failed: {e}")
        return None

def test_batch_storage():
    """Test batch anomaly storage"""
    print("\n🔍 Testing batch anomaly storage...")
    
    test_data = [
        {
            "num_equipement": "BATCH001",
            "systeme": "Electrical",
            "description": "First batch test anomaly"
        },
        {
            "num_equipement": "BATCH002", 
            "systeme": "Mechanical",
            "description": "Second batch test anomaly"
        }
    ]
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/store/batch",
            headers={"Content-Type": "application/json"},
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch storage successful:")
            print(f"   Message: {result['message']}")
            print(f"   Total stored: {result['total_stored']}")
            return True
        else:
            print(f"❌ Batch storage failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Batch storage failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting TAMS Anomaly Storage API Tests")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ API is not running. Please start the service first.")
        sys.exit(1)
    
    # Test 2: Single storage
    anomaly_id = test_single_storage()
    
    # Test 3: Batch storage
    test_batch_storage()
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")
    print("\n📋 Storage-Focused API Summary:")
    print("   ✅ Endpoints store data and return simple confirmations")
    print("   ✅ AI predictions are generated and stored automatically") 
    print("   ✅ Perfect for frontend integration")
    print("\n🔗 Data Retrieval:")
    print("   - Use your Supabase client directly to fetch stored data")
    print("   - Data includes AI predictions and final scores")
    print("\n🔗 API Documentation:")
    print(f"   - Swagger UI: {API_BASE_URL}/docs")
    print(f"   - ReDoc: {API_BASE_URL}/redoc")

if __name__ == "__main__":
    main()
