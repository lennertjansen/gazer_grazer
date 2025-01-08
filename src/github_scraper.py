import os
import requests

GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "your_github_token_here")

def find_top_llm_ai_projects():
    """
    Use GitHub's search API to find top LLM/agent/AI repositories (example).
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
    }
    query = "LLM OR agent OR AI in:name,description,readme stars:>100 sort:stars"
    url = f"{GITHUB_API_URL}/search/repositories?q={query}&per_page=5"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    # Return minimal info: list of {full_name, html_url, ...}
    projects = []
    for item in data["items"]:
        projects.append({
            "name": item["name"],
            "full_name": item["full_name"],
            "url": item["html_url"],
            "description": item.get("description", "")
        })
    return projects
