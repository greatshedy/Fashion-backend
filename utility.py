from argon2 import PasswordHasher
import os
from email.message import EmailMessage
import smtplib
import secrets
from dotenv import load_dotenv
from htmlmessage import mainhtml

load_dotenv()


ph = PasswordHasher()
def hashedpassword(password):
    hased=ph.hash(password)
    return hased


def verifyhash(hashedpassword,password):
    value = ph.verify(hashedpassword,password)
    return value
# ------------------------------
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = str(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
#  Helper: Send Verification Email
# ------------------------------
# ------------------------------
# Helper: Send Verification Email (HTML version)
# ------------------------------
def send_verification_email(to_email: str, otp: str):
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = "mosesgodstime344@gmail.com"
    msg["Subject"] = "Verify your email"

    # Add plain text fallback
    msg.set_content(f"Your OTP is: {otp}")

    # Add HTML content using your mainhtml function
    msg.add_alternative(mainhtml(otp), subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()  # handshake
            # Port 2525: STARTTLS not supported, do NOT call starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False
        
def generate_otp():
    """ generate a secure a 6 digit code..."""
    return str(secrets.randbelow(1000000)).zfill(6)