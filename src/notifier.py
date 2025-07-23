import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Create the Mail object with sender, recipient, subject, and content
def send_mail_via_sendgrid(sender_mail,recipient_email, subject, body_html):
    message = Mail(
        from_email=sender_mail,  # Must be a verified sender identity in SendGrid
        to_emails=recipient_email,
        subject=subject,
        html_content=body_html
    )
    # Initialize the SendGrid client with the API key and send email
    try:
        api_key = os.environ.get("SENDGRID_API_KEY")
        if not api_key:
            print("❌ SendGrid API key not found in environment variables.")
            return False

        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(f"✅ Email sent! Status Code: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False
