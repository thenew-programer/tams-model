import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print("Health Check:", response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_single_prediction():
    """Test single anomaly prediction"""
    test_data = {
        "num_equipement": "EQ001",
        "systeme": "Hydraulic",
        "description": "Pressure drop detected in main valve"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict/single", json=test_data)
        print("Single Prediction Status:", response.status_code)
        if response.status_code == 200:
            print("Single Prediction Response:", response.json())
        else:
            print("Error:", response.text)
        return response.status_code == 200
    except Exception as e:
        print(f"Single prediction test failed: {e}")
        return False

def test_batch_prediction():
    """Test batch anomaly prediction"""
    test_data = [
        {
            "num_equipement": "EQ001",
            "systeme": "Hydraulic",
            "description": "Pressure drop detected in main valve"
        },
        {
            "num_equipement": "EQ002",
            "systeme": "Electrical",
            "description": "Motor overheating issue"
        }
    ]
    
    try:
        response = requests.post(f"{BASE_URL}/predict/batch", json=test_data)
        print("Batch Prediction Status:", response.status_code)
        if response.status_code == 200:
            print("Batch Prediction Response:", response.json())
        else:
            print("Error:", response.text)
        return response.status_code == 200
    except Exception as e:
        print(f"Batch prediction test failed: {e}")
        return False

def test_get_anomalies():
    """Test getting anomalies list"""
    try:
        response = requests.get(f"{BASE_URL}/anomalies")
        print("Get Anomalies Status:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} anomalies")
        else:
            print("Error:", response.text)
        return response.status_code == 200
    except Exception as e:
        print(f"Get anomalies test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing TAMS Anomaly Prediction API...")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Single Prediction", test_single_prediction),
        ("Batch Prediction", test_batch_prediction),
        ("Get Anomalies", test_get_anomalies)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        result = test_func()
        results.append((test_name, result))
        print(f"{test_name}: {'PASS' if result else 'FAIL'}")
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    for test_name, result in results:
        print(f"{test_name}: {'PASS' if result else 'FAIL'}")
    
    total_passed = sum(1 for _, result in results if result)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
