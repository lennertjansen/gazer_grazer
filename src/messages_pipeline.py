import os
from openai import OpenAI
from dotenv import load_dotenv

from db_manager import get_connection, get_leads

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_outreach_message(first_name, project_followed, occupation):
    """
    Use an LLM (OpenAI) to dynamically generate an outreach message.
    """
    system_message = {
        "role": "system",
        "content": "You are a helpful AI assistant who writes short, friendly outreach messages."
    }
    user_message = {
        "role": "user",
        "content": f"""
Write a short, friendly outreach message:
- Person's name: {first_name}
- Project followed: {project_followed}
- Occupation: {occupation}
- Company: Airweave
- Tone: polite, slightly casual, complimentary

Message format:
Hi [first name],
We found that you were following [project] and you work as [occupation] in an LLM/AI-related field.
We're Airweave, etc. and would love to hear your feedback because [you are authority X and we're
lowkey complimenting on your engineering daddy buffness].

Would you be interested in having a chat soon? Let me know, [founder name]
"""
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[system_message, user_message],
    )

    return response.choices[0].message

def message_pipeline():
    conn = get_connection()
    leads = get_leads(conn)

    for lead in leads:
        # Try to parse first name from git_username or from parsed data
        first_name = lead["git_username"].split()[0].capitalize()
        occupation = lead["job_title"] or "Engineer"
        outreach_message = generate_outreach_message(
            first_name=first_name,
            project_followed=lead["project_followed"],
            occupation=occupation
        )
        print("--------------------------------------------------")
        print(f"To: {lead['email'] or lead['git_username']}")
        print(outreach_message)
        print("--------------------------------------------------")

    conn.close()

if __name__ == "__main__":
    message_pipeline()