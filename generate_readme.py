"""
README Generator for LeetCode Solutions Repository
Generates a date-sorted index of all solutions
"""
import os
import re
from datetime import datetime
from github import Github

def fetch_all_solutions_from_repo(repo):
    """Fetch all .md solution files from the repository."""
    try:
        contents = repo.get_contents("")
        solutions = []
        
        for content in contents:
            if content.name.endswith('.md') and content.name.startswith('l') and content.name != 'README.md':
                solutions.append({
                    'filename': content.name,
                    'path': content.path,
                    'sha': content.sha
                })
        
        return solutions
    except Exception as e:
        print(f"Error fetching solutions: {e}")
        return []

def parse_solution_metadata(repo, solution):
    """Parse metadata from a solution file."""
    try:
        # Get file content
        file_content = repo.get_contents(solution['path'])
        content = file_content.decoded_content.decode('utf-8')
        
        # Extract problem number and title from filename
        # Format: l263_UglyNumber.md
        match = re.match(r'l(\d+)_(.+)\.md', solution['filename'])
        if not match:
            return None
        
        problem_num = match.group(1)
        title_pascal = match.group(2)
        
        # Convert PascalCase to Title Case
        title = re.sub(r'([A-Z])', r' \1', title_pascal).strip()
        
        # Extract problem URL from content
        url_match = re.search(r'\*\*LeetCode Problem:\*\* \[.+?\]\((.+?)\)', content)
        problem_url = url_match.group(1) if url_match else f"https://leetcode.com/problems/"
        
        # Extract language from code block
        lang_match = re.search(r'```(\w+)', content)
        language = lang_match.group(1) if lang_match else "Unknown"
        
        # Get commit date (last modified)
        commits = repo.get_commits(path=solution['path'])
        commit_date = commits[0].commit.author.date if commits.totalCount > 0 else datetime.now()
        
        return {
            'number': problem_num,
            'title': title,
            'filename': solution['filename'],
            'url': problem_url,
            'language': language.capitalize(),
            'date': commit_date,
            'date_str': commit_date.strftime('%Y-%m-%d')
        }
    except Exception as e:
        print(f"Error parsing {solution['filename']}: {e}")
        return None

def generate_solutions_readme(solutions_metadata):
    """Generate README content with date-sorted solutions."""
    # Sort by date (newest first)
    sorted_solutions = sorted(solutions_metadata, key=lambda x: x['date'], reverse=True)
    
    # Calculate statistics
    total_problems = len(sorted_solutions)
    languages = set(s['language'] for s in sorted_solutions)
    latest_date = sorted_solutions[0]['date_str'] if sorted_solutions else "N/A"
    
    # Generate README
    readme = f"""
## 🔥 Recent Solutions (Latest First)

| Date | # | Problem | Language | Solution |
|------|---|---------|----------|----------|
"""
    
    # Add solutions table
    for solution in sorted_solutions:
        readme += f"| {solution['date_str']} | {solution['number']} | [{solution['title']}]({solution['url']}) | {solution['language']} | [📝]({solution['filename']}) |\n"
    
    readme += f"""
---
"""
    
    return readme

def update_solutions_readme():
    """Main function to update the README in solutions repository."""
    try:
        g = Github(os.getenv("GITHUB_TOKEN"))
        repo = g.get_repo(os.getenv("TARGET_REPO"))
        
        print("📚 Fetching all solutions from repository...")
        solutions = fetch_all_solutions_from_repo(repo)
        
        if not solutions:
            print("No solutions found in repository")
            return False
        
        print(f"Found {len(solutions)} solution files")
        print("📝 Parsing solution metadata...")
        
        solutions_metadata = []
        for solution in solutions:
            metadata = parse_solution_metadata(repo, solution)
            if metadata:
                solutions_metadata.append(metadata)
        
        print(f"Parsed {len(solutions_metadata)} solutions successfully")
        print("📄 Generating README...")
        
        readme_content = generate_solutions_readme(solutions_metadata)
        
        # Push README to repository
        print("🚀 Updating README in repository...")
        try:
            # Try to get existing README
            readme_file = repo.get_contents("README.md")
            repo.update_file(
                "README.md",
                "Update README with latest solutions",
                readme_content,
                readme_file.sha
            )
            print("✅ README updated successfully!")
        except:
            # Create new README if it doesn't exist
            repo.create_file(
                "README.md",
                "Create README with solutions index",
                readme_content
            )
            print("✅ README created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating README: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # For standalone testing
    from dotenv import load_dotenv
    load_dotenv()
    update_solutions_readme()
