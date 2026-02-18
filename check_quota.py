"""
Check your actual Gemini API quota and limits
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

load_dotenv()

def check_quota():
    """Check available models and test quota"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not found")
            return
        
        print(f"✓ API Key: {api_key[:10]}...")
        genai.configure(api_key=api_key)
        
        print("\n" + "="*60)
        print("📊 Available Models and Their Capabilities")
        print("="*60)
        
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"\n✓ {model.name}")
                print(f"  Display Name: {model.display_name}")
                print(f"  Description: {model.description[:80]}...")
                
        print("\n" + "="*60)
        print("🧪 Testing API with a simple request...")
        print("="*60)
        
        # Try to make a simple request to see if quota is available
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content("Say 'Hello' in one word")
            print(f"✅ SUCCESS! Response: {response.text}")
            print("\n✓ Your API quota is working!")
            
            # Try to get usage metadata if available
            if hasattr(response, 'usage_metadata'):
                print(f"\n📊 Usage Metadata:")
                print(f"  Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"  Response tokens: {response.usage_metadata.candidates_token_count}")
                print(f"  Total tokens: {response.usage_metadata.total_token_count}")
                
        except Exception as e:
            error_str = str(e)
            print(f"❌ FAILED: {error_str}")
            
            if "429" in error_str or "quota" in error_str.lower():
                print("\n⚠️  QUOTA EXCEEDED!")
                print("   Your free tier quota has been exhausted.")
                print("\n💡 Solutions:")
                print("   1. Wait for quota reset (resets daily)")
                print("   2. Check quota at: https://aistudio.google.com/")
                print("   3. Consider upgrading your plan")
                
                # Try to extract retry time if available
                if "retry" in error_str.lower():
                    import re
                    retry_match = re.search(r'(\d+\.?\d*)\s*s', error_str)
                    if retry_match:
                        retry_seconds = float(retry_match.group(1))
                        retry_minutes = retry_seconds / 60
                        print(f"\n⏰ Suggested retry time: {retry_minutes:.1f} minutes")
            else:
                print("\n⚠️  Other API Error")
                print(f"   Error details: {error_str}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*60)
    print("🔍 Gemini API Quota Checker")
    print("="*60)
    check_quota()
    print("\n" + "="*60)
    print("ℹ️  Note: Free tier limits were reduced in Dec 2025")
    print("   Gemini 2.5 Flash: ~20-250 requests/day (varies by region)")
    print("   Check your actual limits at: https://aistudio.google.com/")
    print("="*60)
