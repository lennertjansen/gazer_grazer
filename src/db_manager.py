import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection parameters
DB_PARAMS = {
    'dbname': os.getenv('POSTGRES_DB', 'gazer_grazer'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', ''),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

def get_connection():
    """Create a new database connection"""
    return psycopg2.connect(**DB_PARAMS)

def initialize_db():
    """
    Create the leads table if it doesn't exist.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id SERIAL PRIMARY KEY,
                    git_username VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    linkedin VARCHAR(255),
                    personal_site VARCHAR(255),
                    job_title VARCHAR(255),
                    description TEXT,
                    project_followed VARCHAR(255)
                );
            """)
        conn.commit()
    return conn

def add_lead(conn, lead_data):
    """
    Insert a single lead record into the leads table.
    """
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO leads (
                git_username, email, linkedin, personal_site,
                job_title, description, project_followed
            ) VALUES (
                %(git_username)s, %(email)s, %(linkedin)s, %(personal_site)s,
                %(job_title)s, %(description)s, %(project_followed)s
            ) ON CONFLICT (git_username) DO UPDATE SET
                email = EXCLUDED.email,
                linkedin = EXCLUDED.linkedin,
                personal_site = EXCLUDED.personal_site,
                job_title = EXCLUDED.job_title,
                description = EXCLUDED.description,
                project_followed = EXCLUDED.project_followed
            RETURNING id;
        """, lead_data)
        return cur.fetchone()[0]

def get_leads(conn):
    """
    Retrieve all leads from the database.
    """
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM leads;")
        return [dict(row) for row in cur.fetchall()]