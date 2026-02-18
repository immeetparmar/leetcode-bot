"""
Test script to diagnose Gemini API issues
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def test_gemini_generation():
    """Test if Gemini can generate explanations"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        
        print(f"✓ API Key found: {api_key[:10]}...")
        
        genai.configure(api_key=api_key)
        
        # Try different model names in order of preference
        model_names = ['gemini-2.5-flash', 'gemini-flash-latest', 'gemini-2.0-flash', 'gemini-pro-latest']
        model = None
        
        for model_name in model_names:
            try:
                print(f"\nTrying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                # Test if the model works
                test_response = model.generate_content("Hello")
                print(f"✓ Model {model_name} works!")
                print(f"  Response: {test_response.text[:50]}...")
                
                # Now test with actual code explanation
                print(f"\n🧪 Testing code explanation generation...")
                code = """
class Solution {
    public boolean lemonadeChange(int[] bills) {
        int fiveCount = 0, tenCount = 0;
        
        for (int bill : bills) {
            if (bill == 5) {
                fiveCount++;
            } else if (bill == 10) {
                if (fiveCount == 0) return false;
                fiveCount--;
                tenCount++;
            } else {
                if (tenCount > 0 && fiveCount > 0) {
                    tenCount--;
                    fiveCount--;
                } else if (fiveCount >= 3) {
                    fiveCount -= 3;
                } else {
                    return false;
                }
            }
        }
        return true;
    }
}
"""
                prompt = f"""
I have solved the LeetCode problem "Lemonade Change" in Java.

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

Do NOT repeat the code block in your response.
"""
                
                response = model.generate_content(prompt)
                print(f"✓ Explanation generated successfully!")
                print(f"\n{'='*60}")
                print("Generated Explanation:")
                print('='*60)
                print(response.text)
                print('='*60)
                return True
                
            except Exception as e:
                print(f"✗ Model {model_name} failed: {e}")
                continue
        
        if not model:
            print("\n❌ No available Gemini model found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("🧪 Testing Gemini API for Code Explanation Generation")
    print("="*60)
    success = test_gemini_generation()
    print("\n" + "="*60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed - check errors above")
    print("="*60)
