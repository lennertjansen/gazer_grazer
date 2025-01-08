import os
import re
from firecrawl import FirecrawlApp
from github_scraper import find_top_llm_ai_projects
from db_manager import get_connection, initialize_db, add_lead
from dotenv import load_dotenv

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

def fetch_stargazers_with_firecrawl(repo_url):
    """
    Use Firecrawl to scrape the stargazer page and parse stargazer handles.
    """
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    # Example: crawl the stargazers page
    crawl_result = app.crawl_url(
        repo_url + "/stargazers",
        {
            "limit": 3,  # tune as needed
        },
    )
    # `crawl_result` is typically a dict with "pages" or "results"
    # We'll do a naive parse for demonstration.
    stargazers = set()
    for page_data in crawl_result.get("results", []):
        # page_data["markdown"] might contain user IDs. 
        # This is a naive regex to find GitHub handles in the text:
        text = page_data.get("markdown", "")
        # Something like a handle pattern: "https://github.com/<username>"
        matches = re.findall(r"github\.com/([A-Za-z0-9_-]+)", text)
        for match in matches:
            stargazers.add(match)
    return list(stargazers)

def main_pipeline():
    conn = initialize_db()

    # 1. Find top projects
    projects = find_top_llm_ai_projects()

    # 2. For each project, gather stargazers
    for project in projects:
        print(f"Scraping stargazers for {project['full_name']} ...")
        stargazers = fetch_stargazers_with_firecrawl(project["url"])

        # 3. For each stargazer, scrape related data (like personal websites, job titles, etc.)
        for username in stargazers:
            # In reality, you’d do a deeper Firecrawl or use GitHub’s user API, LinkedIn, etc.
            # Pseudocode below:
            user_data = get_user_data_with_firecrawl_or_api(username)

            # 4. Add each lead to DB
            lead_record = {
                "git_username": username,
                "email": user_data.get("email"),
                "linkedin": user_data.get("linkedin"),
                "personal_site": user_data.get("personal_site"),
                "job_title": user_data.get("job_title"),
                "description": user_data.get("description"),
                "project_followed": project["full_name"],
            }
            add_lead(conn, lead_record)

    conn.close()

def get_user_data_with_firecrawl_or_api(username: str):
    """
    Example function that attempts to gather user info by scraping GitHub profile
    or searching for personal data. 
    This is mostly pseudocode for demonstration.
    """
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    user_profile_url = f"https://github.com/{username}"

    # Try Firecrawl to scrape user profile page
    scrape_result = app.scrape_url(user_profile_url)
    # Parse the returned markdown or text to find email, LinkedIn, job title, etc.
    # This heavily depends on the user’s public GitHub profile content.
    text = scrape_result.get("markdown", "")
    
    # Basic naive extractions for demonstration:
    email = re.search(r"([\w\.-]+@[\w\.-]+)", text)
    linkedin = re.search(r"(https?://(www\.)?linkedin\.com/in/\S+)", text)
    # ...other patterns as needed

    return {
        "email": email.group(0) if email else None,
        "linkedin": linkedin.group(0) if linkedin else None,
        "personal_site": None,  # you can parse further
        "job_title": None,      # e.g., parse from "Title: xxx"
        "description": None,    # parse from user’s summary
    }

if __name__ == "__main__":
    main_pipeline()