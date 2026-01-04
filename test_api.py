import requests
import json

# API base URL
BASE_URL = "http://localhost:8005/api"

# Test the public endpoint first
try:
    response = requests.get(f"{BASE_URL}/transactions/test-public")
    print("Public test endpoint:", response.status_code)
    if response.status_code == 200:
        data = response.json()
        print(f"Total transactions in DB: {data.get('total_transactions', 0)}")
        print("Sample transactions:")
        for tx in data.get('sample_transactions', []):
            print(f"  - {tx}")
    else:
        print("Response:", response.text)
except Exception as e:
    print("Public test endpoint failed:", e)

# Test health endpoint
try:
    response = requests.get(f"{BASE_URL}/health")
    print("Health check:", response.json())
except Exception as e:
    print("Health check failed:", e)
