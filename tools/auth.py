"""
tools/auth.py
-----------------
Registration/login helpers (fixes: "need a registration page and
login page... the user can see only their own history").

Design/scope notes (read this before assuming more than is here):
- Passwords are hashed with bcrypt - this code never stores or
  compares a plaintext password.
- Users sign in with a username and password. A recovery email is
  stored separately and only receives password-reset codes. Configure
  SMTP credentials in the app environment to enable code delivery.
- Session state (who's currently logged in) lives in
  st.session_state["user"] - set on successful login, cleared on
  logout. This is a normal Streamlit session, not a persistent
  browser cookie/JWT - closing the browser tab logs the user out,
  same as the rest of this app's session model.
"""

import re
import secrets
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

import bcrypt

from db import database
from app.config import SMTP_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USE_TLS, SMTP_USER

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{3,32}$")


def is_valid_email(email: str) -> bool:
    return bool(_EMAIL_RE.match((email or "").strip()))


def is_valid_username(username: str) -> bool:
    return bool(_USERNAME_RE.match((username or "").strip()))


def register(username: str, email: str, password: str) -> dict:
    """
    Attempts to register a new user. Returns
    {"success": bool, "message": str, "user": {"id","username","email"} or None}.
    """
    username = (username or "").strip()
    email = (email or "").strip()
    if not is_valid_username(username):
        return {"success": False, "message": "Username must be 3–32 characters and use only letters, numbers, dots, dashes, or underscores.", "user": None}
    if not is_valid_email(email):
        return {"success": False, "message": "Please enter a valid email address.", "user": None}
    if not password or len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters.", "user": None}
    if database.get_user_by_email(email):
        return {"success": False, "message": "An account with this email already exists. Try logging in instead.", "user": None}
    if database.get_user_by_username(username):
        return {"success": False, "message": "That username is already taken.", "user": None}

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    new_id = database.create_user(username, email, password_hash)
    if new_id is None:
        return {"success": False, "message": "Could not create account - the database may be unreachable. Please try again.", "user": None}
    return {"success": True, "message": "Account created.", "user": {"id": new_id, "username": username, "email": email}}


def login(username: str, password: str) -> dict:
    """
    Attempts to authenticate a user. Returns
    {"success": bool, "message": str, "user": {"id","username","email"} or None}.
    """
    username = (username or "").strip()
    user_row = database.get_user_by_username(username)
    if not user_row:
        return {"success": False, "message": "No account found with that username.", "user": None}

    try:
        ok = bcrypt.checkpw(password.encode("utf-8"), user_row["password_hash"].encode("utf-8"))
    except Exception:
        ok = False

    if not ok:
        return {"success": False, "message": "Incorrect password.", "user": None}
    return {"success": True, "message": "Logged in.", "user": {"id": user_row["id"], "username": user_row["username"], "email": user_row["email"]}}


def request_password_reset_code(username: str) -> dict:
    """Emails an expiring, single-use verification code to an account."""
    username = (username or "").strip()
    user_row = database.get_user_by_username(username)
    if not user_row:
        return {"success": False, "message": "No account found with that username."}
    email = user_row["email"]

    if not SMTP_HOST or not SMTP_FROM:
        return {"success": False, "message": "Password reset email is not configured. Add SMTP_HOST and SMTP_FROM (plus credentials if required) to the app secrets."}

    code = f"{secrets.randbelow(1_000_000):06d}"
    expiry = datetime.now() + timedelta(minutes=10)
    code_hash = bcrypt.hashpw(code.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    if not database.store_password_reset_code(email, code_hash, expiry):
        return {"success": False, "message": "Could not prepare a verification code. Please try again."}

    message = EmailMessage()
    message["Subject"] = "Your AI Startup Validator password reset code"
    message["From"] = SMTP_FROM
    message["To"] = email
    message.set_content(
        f"Your verification code is: {code}\n\nIt expires in 10 minutes and can be used once. If you did not request this, you can ignore this email."
    )
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            if SMTP_USE_TLS:
                server.starttls()
            if SMTP_USER:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)
    except Exception:
        database.clear_password_reset_code(email)
        return {"success": False, "message": "We couldn't send the verification email. Please check the SMTP configuration and try again."}
    return {"success": True, "message": "Verification code sent. Check the email used for this account."}


def reset_password_with_code(username: str, code: str, new_password: str) -> dict:
    """Resets a password only after the emailed verification code is proven."""
    user_row = database.get_user_by_username(username)
    if not user_row:
        return {"success": False, "message": "No account found with that username."}
    email = user_row["email"]
    if not new_password or len(new_password) < 6:
        return {"success": False, "message": "New password must be at least 6 characters."}
    record = database.get_password_reset_code(email)
    if not record or record["expires_at"] < datetime.now():
        return {"success": False, "message": "That code has expired or is invalid. Request a new one."}
    try:
        code_matches = bcrypt.checkpw((code or "").strip().encode("utf-8"), record["code_hash"].encode("utf-8"))
    except Exception:
        code_matches = False
    if not code_matches:
        return {"success": False, "message": "That verification code is incorrect."}

    new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    updated = database.update_password(email, new_hash)
    if not updated:
        return {"success": False, "message": "Could not update the password - the database may be unreachable. Please try again."}
    database.clear_password_reset_code(email)
    return {"success": True, "message": "Password updated. You can log in with your new password now."}
