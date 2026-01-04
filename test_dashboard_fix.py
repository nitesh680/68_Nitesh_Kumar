import requests
import json
import time

BASE_URL = "http://localhost:8005/api"

def test_dashboard_performance():
    print("🚀 Testing Dashboard Performance and Fixes...")
    
    # Test 1: Check if backend is responsive
    print("\n1. Testing backend health...")
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        end = time.time()
        print(f"✅ Health check: {response.status_code} ({end-start:.2f}s)")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Test dashboard endpoint performance
    print("\n2. Testing dashboard performance...")
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/analytics/dashboard?month=2026-01", timeout=10)
        end = time.time()
        print(f"⏱️ Dashboard response time: {end-start:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Dashboard Results:")
            print(f"   Total Spend: ${data.get('total_spend', 0):.2f}")
            print(f"   Top Category: {data.get('top_category', 'N/A')}")
            print(f"   Top Category Spend: ${data.get('top_category_spend', 0):.2f}")
            print(f"   Avg Confidence: {data.get('avg_confidence', 'N/A')}")
        else:
            print(f"❌ Dashboard error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
    
    # Test 3: Test AI insights (should be fast now)
    print("\n3. Testing AI insights performance...")
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/insights/summary?month=2026-01", timeout=5)
        end = time.time()
        print(f"⏱️ Insights response time: {end-start:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"🤖 Insights Results:")
            print(f"   AI Enabled: {data.get('ai_enabled', False)}")
            print(f"   Performance Optimized: {data.get('performance_optimized', False)}")
            print(f"   Summary: {data.get('summary', 'N/A')[:100]}...")
        else:
            print(f"❌ Insights error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Insights test failed: {e}")
    
    # Test 4: Test trend endpoint
    print("\n4. Testing trend performance...")
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/analytics/trend", timeout=5)
        end = time.time()
        print(f"⏱️ Trend response time: {end-start:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📈 Trend Results: {len(data)} months of data")
        else:
            print(f"❌ Trend error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Trend test failed: {e}")
    
    print("\n✅ Performance test complete!")

if __name__ == "__main__":
    test_dashboard_performance()
