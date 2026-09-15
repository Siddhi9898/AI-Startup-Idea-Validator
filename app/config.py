"""
Config
------
Central place for API keys and environment configuration.

Works in two environments without any code changes needed between
them:
1. Local development - reads from a .env file via python-dotenv.
2. Streamlit Community Cloud (or any host using Streamlit's secrets
   system) - reads from st.secrets (secrets.toml), since cloud hosts
   don't ship a .env file and secrets.toml values aren't
   automatically exposed as environment variables by Streamlit.

The bridge below copies any matching st.secrets keys into
os.environ (only for keys not already set locally), so every other
module in this project can keep using plain os.getenv(...) either
way - nothing downstream needs to know which environment it's in.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Bridge Streamlit secrets -> environment variables, when available.
# Wrapped defensively: st.secrets raises if there's no secrets.toml
# AND no cloud secrets configured (e.g. running via `python
# pipeline.py` locally, with no Streamlit context at all) - that's a
# normal, expected case here, not an error worth surfacing.
try:
    import streamlit as st
    for _key in (
        "GROQ_API_KEY", "TAVILY_API_KEY", "DATABASE_URL",
        "PG_HOST", "PG_PORT", "PG_DB", "PG_USER", "PG_PASSWORD",
<<<<<<< HEAD
        "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM_EMAIL", "APP_BASE_URL",
=======
        "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD",
        "SMTP_FROM", "SMTP_USE_TLS",
>>>>>>> 14d1a88d30347689a3f1a51ab41d371192e50019
    ):
        if _key in st.secrets and not os.getenv(_key):
            os.environ[_key] = str(st.secrets[_key])
except Exception:
    pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
<<<<<<< HEAD
=======
<<<<<<< Updated upstream
#MODEL_NAME = "llama-3.3-70b-versatile"
=======
>>>>>>> Stashed changes
>>>>>>> 14d1a88d30347689a3f1a51ab41d371192e50019
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
<<<<<<< HEAD
=======
<<<<<<< Updated upstream
=======

# --- Transactional email (password-reset verification codes) ---
# Configure these in .env or Streamlit secrets.  SMTP_FROM defaults to the
# authenticated mailbox when omitted.
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").strip().lower() not in {"0", "false", "no"}
>>>>>>> Stashed changes
>>>>>>> 14d1a88d30347689a3f1a51ab41d371192e50019
