import os
import sys
import json
import subprocess
from dotenv import load_dotenv
from google import genai
from google.genai import types
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

def run_git_diff():
    # Try getting cached/staged diff first
    try:
        result = subprocess.run(['git', 'diff', '--cached'], capture_output=True, text=True, check=True)
        diff = result.stdout.strip()
        if diff:
            return diff
            
        # If no cached diff, try unstaged diff
        result = subprocess.run(['git', 'diff'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error running git diff: {e}{Style.RESET_ALL}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: Git is not installed or not in PATH.{Style.RESET_ALL}")
        sys.exit(1)

def main():
    print(f"{Fore.CYAN}GitScribe CLI - AI Commit Message Generator{Style.RESET_ALL}")
    
    # Load .env from parent directory (root of project)
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print(f"{Fore.RED}Error: GEMINI_API_KEY not found in .env file.{Style.RESET_ALL}")
        sys.exit(1)

    print("Analyzing git diff...")
    diff = run_git_diff()
    if not diff:
        print(f"{Fore.YELLOW}No git diff found. Please make changes or stage them with 'git add'.{Style.RESET_ALL}")
        sys.exit(0)

    # Initialize Gemini client
    client = genai.Client(api_key=api_key)

    system_instruction = """You are an expert developer tool.
Given a git diff, you must generate a Conventional Commit message and a professional GitHub PR description.
Return ONLY valid JSON with this schema:
{
  "commitMessage": "string (The conventional commit message)",
  "prDescription": "string (The PR description including Summary, Changes, and Testing sections)"
}
Do NOT wrap the response in markdown codeblocks like ```json...```, just output the raw JSON object."""

    try:
        print("Generating commit message and PR description...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=diff,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
            ),
        )
        
        result_text = response.text
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        data = json.loads(result_text)
        
        commit_msg = data.get("commitMessage", "")
        pr_desc = data.get("prDescription", "")
        
        print(f"\n{Fore.GREEN}=== Commit Message ==={Style.RESET_ALL}")
        print(f"{Fore.WHITE}{commit_msg}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}=== PR Description ==={Style.RESET_ALL}")
        print(f"{Fore.WHITE}{pr_desc}{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}Error generating content: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()
