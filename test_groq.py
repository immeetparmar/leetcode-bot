"""
Test Groq API integration for LeetCode sync
"""
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

def test_groq_api():
    """Test if Groq API is working"""
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env file")
        print("\n📝 To get a Groq API key:")
        print("   1. Go to https://console.groq.com/")
        print("   2. Sign up (free, no credit card)")
        print("   3. Navigate to 'API Keys'")
        print("   4. Create new API key")
        print("   5. Add to your .env file: GROQ_API_KEY=your_key_here")
        return False
    
    print(f"✓ API Key found: {api_key[:10]}...")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Simple test
    print("\n🧪 Testing Groq API with simple request...")
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": "Say 'Hello from Groq!' in one sentence."}
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ SUCCESS! Response: {message}")
            
            # Show usage info
            if 'usage' in result:
                usage = result['usage']
                print(f"\n📊 Token Usage:")
                print(f"   Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                print(f"   Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                print(f"   Total tokens: {usage.get('total_tokens', 'N/A')}")
            
            # Show rate limit info from headers
            if 'x-ratelimit-remaining-requests' in response.headers:
                print(f"\n⚡ Rate Limit Info:")
                print(f"   Remaining requests: {response.headers.get('x-ratelimit-remaining-requests', 'N/A')}")
                print(f"   Request limit: {response.headers.get('x-ratelimit-limit-requests', 'N/A')}")
            
            return True
        else:
            print(f"❌ API Error {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_code_explanation():
    """Test Groq with actual code explanation"""
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return False
    
    print("\n" + "="*60)
    print("🧪 Testing Code Explanation Generation")
    print("="*60)
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    code = """
class Solution {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (map.containsKey(complement)) {
                return new int[] { map.get(complement), i };
            }
            map.put(nums[i], i);
        }
        return new int[] {};
    }
}
"""
    
    prompt = f"""I have solved the LeetCode problem "Two Sum" in Java.

Here is my code:
```java
{code}
```

Please generate a Markdown response with the following structure:

## Approach

Provide a brief overview of the approach in 1-2 sentences.

Then create a numbered step-by-step breakdown explaining the logic:
1. **Step 1**: Describe what happens first
2. **Step 2**: Describe the next step
(Continue for all major steps in the algorithm)

After the steps, include:
- **Time Complexity**: Explain the time complexity with Big O notation
- **Space Complexity**: Explain the space complexity with Big O notation

## Dry Run

Provide a dry run with ONE good example input that demonstrates the algorithm clearly.

Show the execution in a structured table format with columns for:
- Step number
- Current state of variables
- Action taken
- Result/Output

Use markdown tables for clarity. Make it easy to follow step-by-step.

Do NOT repeat the code block in your response."""
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2048
    }
    
    try:
        print("Generating explanation...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            explanation = result['choices'][0]['message']['content']
            print("✅ Explanation generated successfully!\n")
            print("="*60)
            print("Generated Explanation:")
            print("="*60)
            print(explanation)
            print("="*60)
            return True
        else:
            print(f"❌ API Error {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🚀 Groq API Test Suite")
    print("="*60)
    
    # Test 1: Basic API connectivity
    test1 = test_groq_api()
    
    # Test 2: Code explanation generation
    if test1:
        test2 = test_code_explanation()
    else:
        test2 = False
    
    print("\n" + "="*60)
    print("📊 Test Results:")
    print(f"   Basic API Test: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"   Code Explanation: {'✅ PASS' if test2 else '❌ FAIL'}")
    print("="*60)
    
    if test1 and test2:
        print("\n🎉 All tests passed! Groq is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Make sure AI_PROVIDER=groq in your .env file")
        print("   2. Run: python test_local.py")
        print("   3. Add GROQ_API_KEY to GitHub Secrets")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
