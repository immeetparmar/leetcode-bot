# 🚀 LeetCode to GitHub Sync Automation

Automatically sync your daily LeetCode solutions to a GitHub repository with AI-generated explanations!

## ✨ Features

- 🤖 **AI-Powered Explanations** - Generates detailed step-by-step approach using Groq (Llama 3.3 70B)
- 🚀 **High Quota** - 14,400 free requests/day with Groq API
- 🔄 **Auto-Fallback** - Falls back to Gemini if Groq fails
- 📊 **Dry Run Examples** - Includes structured table-based execution walkthrough
- 🔗 **Clickable Problem Links** - Direct links to LeetCode problems
- 📝 **Multiple Solutions** - Processes all solutions from today + yesterday
- 🎯 **Smart Duplicate Detection** - Skips files with identical code
- ⏰ **Automated Daily Sync** - Runs every day at 11:30 PM IST (18:00 UTC)
- 🏗️ **Two-Repository Architecture** - Separate script and solutions repos
- 🔒 **Secure** - Uses GitHub Secrets for credentials

## 📁 Architecture

- **Script Repository (This Repo)**: Contains the automation script and GitHub Actions workflow
- **Solutions Repository (Target Repo)**: Where your LeetCode solutions are pushed (can be public for portfolio)

## 🛠️ Setup Instructions

### 1. Prerequisites

- GitHub account
- LeetCode account
- **Groq API key** ([Get free key here](https://console.groq.com/)) - **Recommended** (14,400 req/day)
- Google Gemini API key ([Get it here](https://aistudio.google.com/app/apikey)) - Optional fallback (20 req/day)

### 2. Create Target Repository

Create a new repository where your solutions will be stored (e.g., `leetcode-daily` or `leetcode-solutions`).

### 3. Get Required Credentials

#### LeetCode Session Cookie
1. Log in to LeetCode
2. Open browser DevTools (F12)
3. Go to Application/Storage → Cookies → `https://leetcode.com`
4. Copy the value of `LEETCODE_SESSION`

#### GitHub Personal Access Token
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Copy the token

#### Groq API Key (Primary - Recommended)
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up (free, no credit card required)
3. Navigate to "API Keys" → "Create API Key"
4. Copy the key (starts with `gsk_`)

#### Gemini API Key (Optional Fallback)
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 4. Configure GitHub Secrets

In **this repository**, go to `Settings` → `Secrets and variables` → `Actions` and add:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `LEETCODE_SESSION` | Your LeetCode session cookie | `eyJ0eXAiOiJKV1Q...` |
| `GH_TOKEN` | GitHub Personal Access Token | `ghp_xxxxxxxxxxxx` |
| `GROQ_API_KEY` | Groq API key (primary) | `gsk_xxxxxxxxxxxx` |
| `GEMINI_API_KEY` | Gemini API key (fallback, optional) | `AIzaSyxxxxxxxxxx` |
| `TARGET_REPO` | Target repository name | `username/leetcode-daily` |

### 5. Deploy

Push this repository to GitHub. The workflow will automatically run daily at 11:30 PM IST.

## 📋 How It Works

1. **Fetch Submissions** - Gets all accepted submissions from today and yesterday
2. **Generate Explanations** - Uses Groq AI (Llama 3.3 70B) to create detailed explanations with:
   - Step-by-step approach
   - Dry run with example
   - Time & space complexity
   - Auto-fallback to Gemini if Groq fails
3. **Push to GitHub** - Creates/updates markdown files in your solutions repository
4. **Smart Skipping** - Avoids duplicates by comparing code sections

## 📄 Generated File Format

Each solution file includes:

```markdown
# 387. First Unique Character in a String

**LeetCode Problem:** [First Unique Character in a String](https://leetcode.com/problems/first-unique-character-in-a-string/)

## Approach

Brief overview and step-by-step breakdown...

- **Time Complexity**: O(n)
- **Space Complexity**: O(1)

## Dry Run

| Step | Variables | Action | Result |
|------|-----------|--------|--------|
| 1    | freq={}   | Initialize | ... |

## Code
```java
class Solution {
    // Your code here
}
```
```

## 🧪 Local Testing

1. Create a `.env` file:
```bash
LEETCODE_SESSION=your_session_cookie
GITHUB_TOKEN=your_github_token
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key  # Optional fallback
TARGET_REPO=username/repo-name
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Test Groq API:
```bash
python test_groq.py
```

4. Run the full sync test:
```bash
python test_local.py
```

## ⏰ Scheduling Behavior

**Workflow runs daily at 11:30 PM IST**

- **Solved before 11:30 PM** → Pushed same night ✅
- **Solved after 11:30 PM** → Pushed next day ✅
- **Multiple solutions** → All pushed together ✅
- **No solutions today** → Pushes yesterday's pending solutions ✅

## 🔒 Security

- ✅ Credentials stored in GitHub Secrets (encrypted)
- ✅ `.env` file in `.gitignore` (never committed)
- ✅ Minimal token permissions (only `repo` scope)
- ✅ No hardcoded credentials

## 🔑 Session Management (Important!)

LeetCode session cookies expire every **1-2 weeks**. When this happens, the sync will stop working.

### How to Check Session Validity
Run the helper script:
```bash
python check_session.py
```

### How to Fix Locked/Expired Session
If you see "Session Expired" or sync fails:

1. **Log in** to [LeetCode](https://leetcode.com) in your browser
2. **Open DevTools** (F12) → Application → Cookies
3. **Copy** value of `LEETCODE_SESSION`
4. **Update Locally**: Paste new value in `.env`
5. **Update GitHub**: Go to Settings → Secrets → Actions → Update `LEETCODE_SESSION`

## 📊 API Limits

### Groq (Primary)
- **Free Tier**: 14,400 requests/day, 30 requests/minute
- **Model**: Llama 3.3 70B Versatile
- **Speed**: Very fast (specialized LPU hardware)

### Gemini (Fallback)
- **Free Tier**: 20 requests/day (reduced in Dec 2025)
- **Model**: Gemini 2.5 Flash
- **Usage**: Only used if Groq fails

### GitHub Actions
- **Free Tier**: 2000 minutes/month
- **Typical Usage**: ~1 minute/day

**Result**: Well within free tier limits! ✅ Can handle unlimited daily problem solving.

## 🤝 Contributing

Feel free to fork and customize for your needs!

## 📝 License

MIT License - Feel free to use and modify!

---

**Happy Coding!** 🎉
