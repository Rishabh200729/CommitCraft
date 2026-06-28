import httpx
import os
import shutil
import subprocess
from typing import Dict, Any, List

class GithubService:
    @staticmethod
    def clone_repo(repo_url: str, branch: str, token: str, temp_dir: str):
        """
        Clones a repository to a temporary directory using a depth of 1.
        Injects the token into the URL for authentication (works for private repos).
        """
        # Inject token into URL: https://github.com/owner/repo.git -> https://x-access-token:<token>@github.com/owner/repo.git
        if token and repo_url.startswith("https://"):
            auth_url = repo_url.replace("https://", f"https://x-access-token:{token}@")
        else:
            auth_url = repo_url
            
        cmd = [
            "git", "clone", "--depth", "1", "--branch", branch,
            auth_url, temp_dir
        ]
        
        # We don't want the token to end up in logs
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if process.returncode != 0:
            # Mask token in error message
            error_msg = process.stderr
            if token:
                error_msg = error_msg.replace(token, "***")
            raise Exception(f"Git clone failed: {error_msg}")
            
    @staticmethod
    def cleanup_clone(temp_dir: str):
        """
        Removes the cloned repository directory.
        """
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

    @staticmethod
    async def fetch_pr_diff(owner: str, repo: str, pr_number: int, token: str) -> str:
        """
        Fetches the raw diff of a Pull Request using the GitHub API.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.diff"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
            
    @staticmethod
    async def fetch_pr_metadata(owner: str, repo: str, pr_number: int, token: str) -> Dict[str, Any]:
        """
        Fetches metadata (title, body, base branch) for a Pull Request.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return {
                "title": data.get("title", ""),
                "description": data.get("body", ""),
                "base_branch": data.get("base", {}).get("ref", "main"),
                "head_branch": data.get("head", {}).get("ref", ""),
                "clone_url": data.get("base", {}).get("repo", {}).get("clone_url", "")
            }
