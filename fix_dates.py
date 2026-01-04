import requests
import json

BASE_URL = "http://localhost:8005/api"

def fix_transaction_dates():
    """Fix transaction dates to work with 2026-01 insights"""
    
    print("🔧 Fixing transaction dates for January 2026...")
    
    try:
        # Call the fix-dates endpoint
        response = requests.post(f"{BASE_URL}/transactions/fix-dates", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            print(f"📊 Updated: {data['updated']}/{data['total']} transactions")
            
            # Now test the insights
            print("\n🧪 Testing insights with fixed dates...")
            insights_response = requests.get(f"{BASE_URL}/insights/summary?month=2026-01", timeout=30)
            
            if insights_response.status_code == 200:
                insights_data = insights_response.json()
                print(f"📈 Insights Summary: {insights_data['summary']}")
                print(f"💰 Total Spending: ${insights_data.get('total_spending', 0):.2f}")
                print(f"🏆 Top Category: {insights_data.get('breakdown', [{}])[0].get('category', 'N/A')}")
                print(f"📊 Categories Found: {len(insights_data.get('breakdown', []))}")
            else:
                print(f"❌ Insights test failed: {insights_response.status_code}")
                print(f"Response: {insights_response.text}")
                
        else:
            print(f"❌ Fix dates failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_transaction_dates()
