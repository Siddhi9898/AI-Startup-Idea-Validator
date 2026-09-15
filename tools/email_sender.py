"""
tools/email_sender.py
-------------------------
Sends the actual password-reset email (fixes: "do the validation
mail thing - reset your password via your email, then login").

This uses plain SMTP (Python's built-in smtplib) - no third-party
email service required, but you DO need real SMTP credentials for
an account that can send mail, configured via .env:

    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USER=youraddress@gmail.com
    SMTP_PASSWORD=your_16_char_app_password   <- NOT your normal Gmail password
    SMTP_FROM_EMAIL=youraddress@gmail.com
    APP_BASE_URL=http://localhost:8501        <- change to your deployed URL in production

For Gmail specifically: enable 2-Step Verification on the account,
then create an "App Password" at https://myaccount.google.com/apppasswords
and use THAT as SMTP_PASSWORD - Gmail rejects your normal login
password for SMTP. Any other SMTP provider (Outlook, SendGrid's SMTP
relay, your own mail server, etc.) works the same way - just point
SMTP_HOST/SMTP_PORT at it.

Until these are set, send_password_reset_email() fails clearly and
tells the caller why, instead of pretending an email went out.
"""

import os
import smtplib
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL") or SMTP_USER
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8501")


def is_configured() -> bool:
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def send_password_reset_email(to_email: str, reset_token: str) -> dict:
    """Sends the actual reset email with a link containing the raw
    token. Returns {"success": bool, "message": str}."""
    if not is_configured():
        return {
            "success": False,
            "message": (
                "Email sending isn't configured yet - set SMTP_HOST, SMTP_USER, "
                "and SMTP_PASSWORD in .env (see tools/email_sender.py for a "
                "Gmail example) before this can send real reset emails."
            ),
        }

    reset_link = f"{APP_BASE_URL}/?reset_token={reset_token}"
    body = f"""Hello,

We received a request to reset your password for the AI Startup Idea Validator.

Click the link below to set a new password. This link is valid for 30 minutes:

{reset_link}

If you didn't request this, you can safely ignore this email - your password won't change.
"""
    msg = MIMEText(body)
    msg["Subject"] = "Reset your password - AI Startup Idea Validator"
    msg["From"] = SMTP_FROM_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM_EMAIL, [to_email], msg.as_string())
        return {"success": True, "message": "Reset email sent - check your inbox."}
    except Exception as e:
        return {"success": False, "message": f"Could not send email: {e}"}
