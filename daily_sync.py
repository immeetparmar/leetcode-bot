import os
import requests
import datetime
import json
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
from github import Github

# --- CONFIGURATION ---
# Best practice: Load these from Environment Variables
LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# The repository where you want to save the solutions (can be different from this repo)
TARGET_REPO = os.getenv("TARGET_REPO")  # e.g., "your-username/leetcode-solutions"

# AI Provider Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").lower()  # groq, gemini, or auto (tries groq then gemini)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QUIET_MODE = os.getenv("QUIET_MODE", "false").lower() == "true"

# AI API retry and rate limiting configuration
AI_RETRY_ATTEMPTS = int(os.getenv("AI_RETRY_ATTEMPTS", "3"))
AI_RETRY_DELAY = int(os.getenv("AI_RETRY_DELAY", "5"))  # seconds
SUBMISSION_DELAY = int(os.getenv("SUBMISSION_DELAY", "2"))  # seconds between processing submissions

def log(message, force=False):
    """Print message only if not in quiet mode, or if force=True"""
    if not QUIET_MODE or force:
        print(message)

def get_todays_accepted_submissions():
    """Fetches all accepted submissions from today, or yesterday if today is empty."""
    url = "https://leetcode.com/graphql"
    headers = {
        "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    # Query for the latest submission list
    query_list = """
    query recentAcSubmissions($username: String!, $limit: Int!) {
        recentAcSubmissionList(username: $username, limit: $limit) {
            id
            title
            titleSlug
            timestamp
        }
    }
    """
    
    # We need your username first. This query fetches your profile info.
    query_user = """
    query globalData {
        userStatus {
            username
        }
    }
    """
    
    try:
        # Get Username
        user_resp = requests.post(url, json={'query': query_user}, headers=headers).json()
        username = user_resp['data']['userStatus']['username']

        # Get recent submissions (fetch more to ensure we get all from today)
        list_resp = requests.post(url, json={'query': query_list, 'variables': {'username': username, 'limit': 20}}, headers=headers).json()
        all_submissions = list_resp['data']['recentAcSubmissionList']

        if not all_submissions:
            log("No submissions found")
            return []

        # Get today and yesterday dates
        today = datetime.datetime.now().date()
        yesterday = today - datetime.timedelta(days=1)
        
        # Filter submissions by date
        todays_submissions = []
        yesterdays_submissions = []
        
        for submission in all_submissions:
            submission_time = datetime.datetime.fromtimestamp(int(submission['timestamp']))
            submission_date = submission_time.date()
            
            if submission_date == today:
                todays_submissions.append(submission)
            elif submission_date == yesterday:
                yesterdays_submissions.append(submission)
        
        # Decide which submissions to return
        combined_submissions = todays_submissions + yesterdays_submissions
        
        if combined_submissions:
            if todays_submissions and yesterdays_submissions:
                log(f"✅ Found {len(todays_submissions)} submission(s) from today ({today})")
                log(f"✅ Found {len(yesterdays_submissions)} submission(s) from yesterday ({yesterday})")
                log(f"📦 Total: {len(combined_submissions)} submission(s) to process")
            elif todays_submissions:
                log(f"✅ Found {len(todays_submissions)} submission(s) from today ({today})")
            elif yesterdays_submissions:
                log(f"⏰ No submissions from today. Found {len(yesterdays_submissions)} submission(s) from yesterday ({yesterday})")
            
            return combined_submissions
        else:
            log(f"⏭️  No submissions from today or yesterday")
            return []
            
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "403" in error_msg or "Unauthenticated" in error_msg:
            log("\n❌ LEETCODE SESSION EXPIRED OR INVALID", force=True)
            log("   Please update your LEETCODE_SESSION cookie:", force=True)
            log("   1. Login to LeetCode", force=True)
            log("   2. Get new cookie from browser dev tools", force=True)
            log("   3. Update .env file (local)", force=True)
            log("   4. Update GitHub Secret (remote)", force=True)
        else:
            log(f"Error fetching from LeetCode: {e}", force=True)
        return []

def get_submission_code(submission_id):
    """Fetches the actual code and question ID for a specific submission."""
    url = "https://leetcode.com/graphql"
    headers = {
        "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    query_details = """
    query submissionDetails($submissionId: Int!) {
        submissionDetails(submissionId: $submissionId) {
            code
            lang {
                name
            }
            question {
                questionFrontendId
            }
        }
    }
    """
    
    try:
        # Ensure submission_id is an integer
        submission_id = int(submission_id)
        resp = requests.post(url, json={'query': query_details, 'variables': {'submissionId': submission_id}}, headers=headers).json()
        
        # Check for errors in response
        if 'errors' in resp:
            log(f"GraphQL Error: {resp['errors']}", force=True)
            return None
        
        if 'data' not in resp or resp['data'] is None:
            log(f"No data in response: {resp}", force=True)
            return None
            
        return resp['data']['submissionDetails']
    except Exception as e:
        log(f"Error fetching submission code: {e}", force=True)
        return None

def generate_explanation_groq(code, language, question_title):
    """Generate explanation using Groq API (14,400 req/day free tier)."""
    import time
    
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not configured")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Use Llama 3.3 70B - excellent for code explanations
    model = "llama-3.3-70b-versatile"
    
    prompt = f"""I have solved the LeetCode problem "{question_title}" in {language}.

Here is my code:
```{language}
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
    
    # Retry logic with exponential backoff
    last_error = None
    for attempt in range(1, AI_RETRY_ATTEMPTS + 1):
        try:
            log(f"  Attempt {attempt}/{AI_RETRY_ATTEMPTS} (Groq)...")
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2048
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                explanation = result['choices'][0]['message']['content']
                log(f"  ✓ Explanation generated successfully with Groq!")
                return explanation
            elif response.status_code == 429:
                # Rate limit hit
                last_error = Exception(f"Rate limit: {response.text}")
                log(f"  ⚠️  Groq rate limit hit (attempt {attempt}/{AI_RETRY_ATTEMPTS})", force=True)
                
                if attempt < AI_RETRY_ATTEMPTS:
                    wait_time = AI_RETRY_DELAY * (2 ** (attempt - 1))
                    log(f"  ⏰ Waiting {wait_time}s before retry...", force=True)
                    time.sleep(wait_time)
            else:
                # Other error
                error_msg = response.text[:200]
                raise Exception(f"Groq API error {response.status_code}: {error_msg}")
                
        except requests.exceptions.Timeout:
            last_error = Exception("Request timeout")
            log(f"  ⚠️  Request timeout (attempt {attempt}/{AI_RETRY_ATTEMPTS})", force=True)
            if attempt < AI_RETRY_ATTEMPTS:
                time.sleep(AI_RETRY_DELAY)
        except Exception as e:
            last_error = e
            log(f"  ❌ Groq error: {str(e)[:100]}", force=True)
            if attempt < AI_RETRY_ATTEMPTS:
                time.sleep(AI_RETRY_DELAY)
    
    # All retries failed
    raise last_error if last_error else Exception("Unknown error")

def generate_explanation_gemini(code, language, question_title):
    """Generate explanation using Gemini API (20 req/day free tier)."""
    import time
    
    if not GENAI_AVAILABLE:
        raise Exception("google-generativeai package not installed")
    
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY not configured")
    
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Try different model names in order of preference
    model_names = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest']
    model = None
    
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            log(f"Using Gemini model: {model_name}")
            break
        except Exception as e:
            log(f"Model {model_name} not available: {str(e)[:50]}")
            continue
    
    if not model:
        raise Exception("No available Gemini model found")
    
    prompt = f"""I have solved the LeetCode problem "{question_title}" in {language}.

Here is my code:
```{language}
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
    
    # Retry logic with exponential backoff
    last_error = None
    for attempt in range(1, AI_RETRY_ATTEMPTS + 1):
        try:
            log(f"  Attempt {attempt}/{AI_RETRY_ATTEMPTS} (Gemini)...")
            response = model.generate_content(prompt)
            log(f"  ✓ Explanation generated successfully with Gemini!")
            return response.text
        except Exception as e:
            last_error = e
            error_str = str(e)
            
            # Check if it's a quota/rate limit error
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                log(f"  ⚠️  Gemini rate limit hit (attempt {attempt}/{AI_RETRY_ATTEMPTS})", force=True)
                
                if attempt < AI_RETRY_ATTEMPTS:
                    wait_time = AI_RETRY_DELAY * (2 ** (attempt - 1))
                    log(f"  ⏰ Waiting {wait_time}s before retry...", force=True)
                    time.sleep(wait_time)
            else:
                # Non-quota error, don't retry
                log(f"  ❌ Gemini error: {error_str[:100]}", force=True)
                raise e
    
    # All retries failed
    raise last_error if last_error else Exception("Unknown error")

def generate_explanation(code, language, question_title):
    """Generate explanation using configured AI provider with fallback support."""
    import time
    
    log(f"🤖 Generating AI explanation using provider: {AI_PROVIDER}")
    
    # Determine which providers to try based on configuration
    providers_to_try = []
    
    if AI_PROVIDER == "groq":
        providers_to_try = ["groq", "gemini"]  # Try Groq first, fallback to Gemini
    elif AI_PROVIDER == "gemini":
        providers_to_try = ["gemini"]  # Only Gemini
    elif AI_PROVIDER == "auto":
        providers_to_try = ["groq", "gemini"]  # Try both, Groq first
    else:
        log(f"⚠️  Unknown AI_PROVIDER: {AI_PROVIDER}, defaulting to auto", force=True)
        providers_to_try = ["groq", "gemini"]
    
    # Try each provider in order
    last_error = None
    for provider in providers_to_try:
        try:
            if provider == "groq" and GROQ_API_KEY:
                log(f"  Trying Groq API...")
                return generate_explanation_groq(code, language, question_title)
            elif provider == "gemini" and GEMINI_API_KEY:
                log(f"  Trying Gemini API...")
                return generate_explanation_gemini(code, language, question_title)
            else:
                log(f"  Skipping {provider} (API key not configured)")
                continue
        except Exception as e:
            last_error = e
            error_msg = str(e)[:100]
            log(f"  ❌ {provider.capitalize()} failed: {error_msg}", force=True)
            
            # If there are more providers to try, continue
            if provider != providers_to_try[-1]:
                log(f"  → Trying next provider...", force=True)
                time.sleep(1)  # Brief pause before trying next provider
                continue
    
    # All providers failed, return fallback
    error_reason = str(last_error)[:100] if last_error else "No AI provider configured"
    log(f"❌ All AI providers failed, using fallback explanation", force=True)
    return generate_fallback_explanation(question_title, error_reason)

def generate_fallback_explanation(question_title, error_reason):
    """Generate a fallback explanation when AI generation fails."""
    return f"""## Approach

This solution solves the "{question_title}" problem.

**Time Complexity:** To be analyzed  
**Space Complexity:** To be analyzed

---

> [!NOTE]
> **AI explanation generation failed**  
> Reason: {error_reason}
> 
> Please add a detailed explanation manually, or wait for API quota to reset and re-run the sync.
"""

def push_to_github(filename, content, commit_message):
    """Pushes the file to the specified GitHub repository."""
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(TARGET_REPO)
    
    try:
        # Try to get the file to see if it exists
        contents = repo.get_contents(filename)
        existing_content = contents.decoded_content.decode('utf-8')
        
        # Extract just the code section from both contents to compare
        # This avoids re-pushing if only the AI explanation changed
        def extract_code(file_content):
            """Extract the code block from markdown content"""
            if "## Code" in file_content:
                code_section = file_content.split("## Code", 1)[1]
                return code_section.strip()
            return file_content
        
        existing_code = extract_code(existing_content)
        new_code = extract_code(content)
        
        if existing_code == new_code:
            log(f"⏭️  Skipping: File '{filename}' already exists with same code")
            return False
        else:
            # Update if code is different
            repo.update_file(contents.path, commit_message, content, contents.sha)
            log(f"✅ Updated file: {filename} (code changed)")
            return True
    except:
        # If it doesn't exist, create it
        repo.create_file(filename, commit_message, content)
        log(f"✅ Created file: {filename}")
        return True

def main():
    log("="*60)
    log("🚀 LeetCode to GitHub Sync Starting...")
    log("="*60)
    
    # 1. Get Today's Submissions (or yesterday's if today is empty)
    submissions = get_todays_accepted_submissions()
    
    if not submissions:
        log("\n✓ No submissions to process")
        return
    
    log(f"\n📝 Processing {len(submissions)} submission(s)...\n")
    
    pushed_count = 0
    skipped_count = 0
    
    # Process each submission
    for idx, submission in enumerate(submissions, 1):
        log(f"\n[{idx}/{len(submissions)}] Processing: {submission['title']}")
        log("-" * 60)
        
        # Add delay between submissions to avoid rate limits (except for first submission)
        if idx > 1 and SUBMISSION_DELAY > 0:
            import time
            log(f"⏰ Waiting {SUBMISSION_DELAY}s to avoid rate limits...")
            time.sleep(SUBMISSION_DELAY)
        
        # 2. Get Code and Question ID
        details = get_submission_code(submission['id'])
        if not details:
            log(f"❌ Failed to fetch submission details, skipping...", force=True)
            skipped_count += 1
            continue
            
        code = details['code']
        lang = details['lang']['name']
        q_id = details['question']['questionFrontendId']
        title = submission['title']
        
        # 3. Format Filename: l{id}_{PascalCaseTitle}
        sanitized_title = title.replace(" ", "")
        filename = f"l{q_id}_{sanitized_title}.md"
        
        # 4. Generate Content (Approach + Code)
        log("🤖 Generating AI explanation...")
        explanation = generate_explanation(code, lang, title)
        
        # Create the problem URL using titleSlug
        problem_url = f"https://leetcode.com/problems/{submission['titleSlug']}/"
        
        final_content = f"# {q_id}. {title}\n\n"
        final_content += f"**LeetCode Problem:** [{title}]({problem_url})\n\n"
        final_content += explanation
        final_content += f"\n## Code\n```{lang}\n{code}\n```"

        # 5. Commit and Push
        commit_msg = f"Solved: l{q_id}_{sanitized_title}"
        pushed = push_to_github(filename, final_content, commit_msg)
        
        if pushed:
            pushed_count += 1
        else:
            skipped_count += 1
    
    # Summary
    log("\n" + "="*60)
    log("📊 Summary:")
    log(f"   ✅ Pushed: {pushed_count}")
    log(f"   ⏭️  Skipped: {skipped_count}")
    log("="*60)
    
    # Update README if any files were pushed
    if pushed_count > 0:
        log("\n📚 Updating solutions README...")
        try:
            from generate_readme import update_solutions_readme
            if update_solutions_readme():
                log("✅ Solutions README updated!")
            else:
                log("⚠️  README update failed (non-critical)", force=True)
        except Exception as e:
            log(f"⚠️  README update error: {str(e)[:100]} (non-critical)", force=True)

if __name__ == "__main__":
    main()
