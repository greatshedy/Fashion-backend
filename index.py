import os
import resend

resend.api_key = os.environ.get("RESEND_API_KEY")
def send_email(to_email: str, subject: str, html_content: str):
    try:
        params: resend.Emails.SendParams = {
            # Make sure this 'from' email is verified on your Resend dashboard
            "from": "Acme <onboarding@resend.dev>", 
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        
        email = resend.Emails.send(params)
        print(f"Email successfully sent to {to_email}: {email}")
        return email
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
        return None