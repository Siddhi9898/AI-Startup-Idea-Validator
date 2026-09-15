"""
tools/auth.py
-----------------
Registration/login/password-reset helpers (fixes: "need a
registration page and login page... the user can see only their own
history"; "reset your password via a real email link, then login";
"ask security questions at registration so a forgotten password can
be reset by answering one").

Design/scope notes (read this before assuming more than is here):
- Passwords are hashed with bcrypt - this code never stores or
  compares a plaintext password. Security question ANSWERS are
  hashed the exact same way - never stored or compared in plaintext
  either.
- Registration itself still does NOT verify the email is real -
  "real mail" there means the founder's real email is used as their
  account identifier, not that a verification email is sent on
  signup.
- TWO independent password-reset paths exist, and the founder picks
  whichever works for them:
  1. Email link (request_password_reset / confirm_password_reset) -
     sends a genuine one-time, time-limited token via
     tools/email_sender.py, but only works once real SMTP
     credentials are configured in .env (see that file's docstring).
  2. Security question (get_security_question /
     reset_password_with_security_answer) - needs no external
     configuration at all, works immediately. This is why every
     registration requires choosing a question and answering it.
- Session state (who's currently logged in) lives in
  st.session_state["user"] - set on successful login, cleared on
  logout. This is a normal Streamlit session, not a persistent
  browser cookie/JWT - closing the browser tab logs the user out,
  same as the rest of this app's session model.
"""

import re
import secrets
import hashlib
import socket
from datetime import datetime, timedelta

import bcrypt

from db import database
from tools import email_sender

# Stricter format check than a bare "has @ and a dot" - rejects
# obviously malformed input (spaces, missing TLD, illegal characters)
# before we even bother with a DNS lookup.
_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
)

# A DNS lookup alone can't catch every typo - some common misspellings
# of major providers are themselves registered, real, resolvable
# domains (often typo-squats), so they'd otherwise sail through the
# DNS check above. This closes that specific, common gap.
_COMMON_TYPO_DOMAINS = {
    "gmial.com", "gmal.com", "gmai.com", "gnail.com", "gmail.co", "gmailc.om",
    "yaho.com", "yahooo.com", "yhoo.com", "yahoo.co",
    "hotmial.com", "hotmil.com", "hotmai.com", "hotmail.co",
    "outlok.com", "outllook.com", "outlook.co",
    "iclould.com", "icoud.com", "icloud.co",
}

# Fixes: "ask a few security questions at registration (mother's
# maiden name, pet's name, etc.) so a forgotten password can be reset
# by answering one, instead of only via an emailed link." This is a
# SECOND, always-available reset path alongside the email-link flow
# above - it needs no SMTP configuration at all, so it works
# immediately even before you set up real email sending.
SECURITY_QUESTIONS = [
    "What is your mother's maiden name?",
    "What was the name of your first pet?",
    "What city were you born in?",
    "What was the name of your first school?",
    "What is your favorite childhood nickname?",
    "What was the make or model of your first car?",
]


def _normalize_answer(answer: str) -> str:
    """Security answers are compared case- and whitespace-insensitively
    - "Fluffy", "fluffy ", and "FLUFFY" should all match, since a
    human isn't going to remember their own capitalization choice
    months later."""
    return (answer or "").strip().lower()


def is_valid_email(email: str) -> bool:
    """
    Fixes: "if the user gives an invalid email, ask them to enter a
    valid one" - the old check accepted anything shaped like x@y.z,
    including typos like "gmial.com" that don't exist as a domain at
    all. This adds a real DNS lookup on top of a stricter regex: the
    domain must actually resolve, which catches typo'd/fake domains
    the regex alone can't.

    Trade-off, stated plainly: the DNS lookup can't tell "this domain
    doesn't exist" apart from "no network access right now" with full
    certainty - a machine with no internet connectivity at all could
    see valid emails rejected here. That's judged an acceptable
    trade-off for catching real typos, since registration/login
    already require a live Postgres connection anyway.
    """
    email = (email or "").strip()
    if not _EMAIL_RE.match(email):
        return False
    domain = email.rsplit("@", 1)[-1].lower()
    if domain in _COMMON_TYPO_DOMAINS:
        return False
    try:
        socket.getaddrinfo(domain, None)
        return True
    except socket.gaierror:
        return False
    except Exception:
        return True  # any other error (e.g. DNS server unreachable) - fail open


def register(email: str, password: str, security_question: str, security_answer: str) -> dict:
    """
    Attempts to register a new user. security_question must be one of
    SECURITY_QUESTIONS, and security_answer must be non-empty - both
    are required so every account has a working, no-SMTP-needed
    fallback for password reset. Returns
    {"success": bool, "message": str, "user": {"id","email"} or None}.
    """
    email = (email or "").strip()
    if not is_valid_email(email):
        return {"success": False, "message": "Please enter a valid email address.", "user": None}
    if not password or len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters.", "user": None}
    if security_question not in SECURITY_QUESTIONS:
        return {"success": False, "message": "Please choose one of the listed security questions.", "user": None}
    if not security_answer or not security_answer.strip():
        return {"success": False, "message": "Please answer your chosen security question - it's used to reset your password later.", "user": None}
    if database.get_user_by_email(email):
        return {"success": False, "message": "An account with this email already exists. Try logging in instead.", "user": None}

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    answer_hash = bcrypt.hashpw(_normalize_answer(security_answer).encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    new_id = database.create_user(email, password_hash, security_question, answer_hash)
    if new_id is None:
        return {"success": False, "message": "Could not create account - the database may be unreachable. Please try again.", "user": None}
    return {"success": True, "message": "Account created.", "user": {"id": new_id, "email": email}}


def login(email: str, password: str) -> dict:
    """
    Attempts to authenticate a user. Returns
    {"success": bool, "message": str, "user": {"id","email"} or None}.
    """
    email = (email or "").strip()
    user_row = database.get_user_by_email(email)
    if not user_row:
        return {"success": False, "message": "No account found with that email.", "user": None}

    try:
        ok = bcrypt.checkpw(password.encode("utf-8"), user_row["password_hash"].encode("utf-8"))
    except Exception:
        ok = False

    if not ok:
        return {"success": False, "message": "Incorrect password.", "user": None}
    return {"success": True, "message": "Logged in.", "user": {"id": user_row["id"], "email": user_row["email"]}}


def request_password_reset(email: str) -> dict:
    """
    Step 1 of the real "Forgot Password" flow: if the email belongs
    to a registered account, generates a secure, time-limited (30
    minute) one-time token, stores only its HASH in the database, and
    emails the raw token (as a link) to the address on file via
    tools/email_sender.py. Returns {"success": bool, "message": str}.
    """
    email = (email or "").strip()
    if not is_valid_email(email):
        return {"success": False, "message": "Please enter a valid email address."}

    user_row = database.get_user_by_email(email)
    if not user_row:
        return {"success": False, "message": "No account found with that email."}

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    expires_at = datetime.now() + timedelta(minutes=30)

    token_id = database.create_password_reset_token(user_row["id"], token_hash, expires_at)
    if token_id is None:
        return {"success": False, "message": "Could not start password reset - the database may be unreachable. Please try again."}

    email_result = email_sender.send_password_reset_email(email, raw_token)
    if not email_result["success"]:
        return {"success": False, "message": email_result["message"]}
    return {"success": True, "message": "A password reset link has been sent to your email. It's valid for 30 minutes."}


def confirm_password_reset(raw_token: str, new_password: str) -> dict:
    """
    Step 2: called when the founder arrives back at the app via the
    emailed link (?reset_token=...). Verifies the token is real,
    unused, and not expired, sets the new password, and consumes the
    token so the same link can't be used twice. Returns
    {"success": bool, "message": str}.
    """
    if not new_password or len(new_password) < 6:
        return {"success": False, "message": "New password must be at least 6 characters."}
    if not raw_token:
        return {"success": False, "message": "Missing or invalid reset link."}

    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    token_row = database.get_valid_reset_token(token_hash)
    if not token_row:
        return {"success": False, "message": "This reset link is invalid, expired, or has already been used. Please request a new one."}

    new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    updated = database.update_password(token_row["email"], new_hash)
    if not updated:
        return {"success": False, "message": "Could not update the password - the database may be unreachable. Please try again."}

    database.mark_reset_token_used(token_row["id"])
    return {"success": True, "message": "Password updated. You can log in with your new password now."}


def get_security_question(email: str) -> dict:
    """
    Step 1 of the no-SMTP-needed reset path: looks up the security
    question the founder chose at registration. Returns
    {"success": bool, "message": str, "question": str or None}.
    """
    email = (email or "").strip()
    if not is_valid_email(email):
        return {"success": False, "message": "Please enter a valid email address.", "question": None}

    user_row = database.get_user_by_email(email)
    if not user_row:
        return {"success": False, "message": "No account found with that email.", "question": None}
    if not user_row.get("security_question"):
        return {
            "success": False,
            "message": "This account doesn't have a security question on file (it may predate this feature). Use the email reset link instead.",
            "question": None,
        }
    return {"success": True, "message": "", "question": user_row["security_question"]}


def reset_password_with_security_answer(email: str, answer: str, new_password: str) -> dict:
    """
    Step 2: verifies the answer against the hash stored at
    registration, then sets the new password. Returns
    {"success": bool, "message": str}.
    """
    email = (email or "").strip()
    if not new_password or len(new_password) < 6:
        return {"success": False, "message": "New password must be at least 6 characters."}

    user_row = database.get_user_by_email(email)
    if not user_row or not user_row.get("security_answer_hash"):
        return {"success": False, "message": "No account with a security question found for that email."}

    try:
        answer_ok = bcrypt.checkpw(
            _normalize_answer(answer).encode("utf-8"),
            user_row["security_answer_hash"].encode("utf-8"),
        )
    except Exception:
        answer_ok = False

    if not answer_ok:
        return {"success": False, "message": "That answer doesn't match what we have on file."}

    new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    updated = database.update_password(email, new_hash)
    if not updated:
        return {"success": False, "message": "Could not update the password - the database may be unreachable. Please try again."}
    return {"success": True, "message": "Password updated. You can log in with your new password now."}
