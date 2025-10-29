"""
Quick test to verify Bearer Token authentication is working.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_authentication_flow():
    """Test the complete authentication flow."""
    
    print("="*80)
    print("  Testing Bearer Token Authentication Fix")
    print("="*80)
    
    # Step 1: Generate token
    print("\n1️⃣  Generating JWT token...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"api_key": "demo-api-key-12345"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to generate token: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        token_data = response.json()
        token = token_data['access_token']
        print(f"✅ Token generated successfully")
        print(f"   Token (first 50 chars): {token[:50]}...")
        
    except Exception as e:
        print(f"❌ Error generating token: {str(e)}")
        return False
    
    # Step 2: Test protected endpoint with token
    print("\n2️⃣  Testing protected endpoint with Bearer token...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/invoices?count=3",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to access protected endpoint: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        data = response.json()
        print(f"✅ Successfully accessed protected endpoint")
        print(f"   Received {data['count']} invoices")
        
    except Exception as e:
        print(f"❌ Error accessing protected endpoint: {str(e)}")
        return False
    
    # Step 3: Test verify endpoint
    print("\n3️⃣  Verifying token at /auth/verify...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/verify",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Token verification failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        verify_data = response.json()
        print(f"✅ Token verified successfully")
        print(f"   Token info: {json.dumps(verify_data['token_info'], indent=2)}")
        
    except Exception as e:
        print(f"❌ Error verifying token: {str(e)}")
        return False
    
    # Step 4: Test without token (should fail)
    print("\n4️⃣  Testing protected endpoint WITHOUT token (should fail)...")
    try:
        response = requests.get(f"{BASE_URL}/invoices?count=3")
        
        if response.status_code == 401 or response.status_code == 403:
            print(f"✅ Correctly rejected request without token (status: {response.status_code})")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "="*80)
    print("  ✅ All tests passed! Bearer Token authentication is working!")
    print("="*80)
    return True

if __name__ == "__main__":
    try:
        # Check server is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please ensure it's running on http://localhost:8000")
        exit(1)
    
    # Run tests
    success = test_authentication_flow()
    
    if success:
        print("\n💡 You can now use Bearer tokens to access protected endpoints!")
        print("\nExample:")
        print("  1. Generate token: POST /auth/token")
        print("  2. Use in header: Authorization: Bearer <your-token>")
        print("  3. Access endpoint: GET /invoices?count=5")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
