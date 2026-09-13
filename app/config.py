"""
Config
------
Central place for API keys and environment configuration.
"""

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
#MODEL_NAME = "llama-3.3-70b-versatile"
MODEL_NAME = "openai/gpt-oss-120b"

# --- PostgreSQL (Idea History persistence) ---
# Either set a single DATABASE_URL (e.g. postgresql://user:pass@host:5432/dbname)
# or the individual PG* variables below - DATABASE_URL wins if both are set.
DATABASE_URL = os.getenv("DATABASE_URL")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB", "startup_validator")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")
