"""
Check LeetCode Session Validity
Run this script to verify if your LEETCODE_SESSION cookie is still valid.
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")

def check_session():
    print("Locked & Loaded: Checking LeetCode Session Validity...")
    print("-" * 50)
    
    if not LEETCODE_SESSION:
        print("❌ LEETCODE_SESSION not found in .env file")
        return False
        
    print(f"🔑 Session Key: {LEETCODE_SESSION[:10]}...{LEETCODE_SESSION[-5:]}")
    
    url = "https://leetcode.com/graphql"
    headers = {
        "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    # Simple query to get user profile (requires auth)
    query = """
    query globalData {
        userStatus {
            isSignedIn
            username
        }
    }
    """
    
    try:
        response = requests.post(url, json={"query": query}, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            user_status = data.get("data", {}).get("userStatus", {})
            
            if user_status.get("isSignedIn"):
                print(f"✅ SUCCESS! Logged in as: {user_status.get('username')}")
                print("   Your session is valid and ready for syncing.")
                return True
            else:
                print("❌ Session Expired or Invalid (Not signed in)")
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        
    print("-" * 50)
    print("📝 HOW TO FIX:")
    print("1. Log in to LeetCode in your browser")
    print("2. Open Developer Tools (F12) -> Application -> Cookies")
    print("3. Copy the value of 'LEETCODE_SESSION'")
    print("4. Update your .env file locally")
    print("5. IMPORTANT: Update GitHub Secrets (Settings -> Secrets -> Actions)")
    print("-" * 50)
    return False

if __name__ == "__main__":
    check_session()
