from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv

# Load env from root
load_dotenv()

def send_email_alert(product_url, old_price, new_price):
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("FROM_EMAIL")
    to_email = from_email  # sending to yourself

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject="🚨 Price Drop Alert!",
        html_content=f"""
        <h2>🚨 Price Dropped!</h2>
        <p><strong>Product:</strong> {product_url}</p>
        <p><strong>Old Price:</strong> ₹{old_price}</p>
        <p><strong>New Price:</strong> ₹{new_price}</p>
        """
    )

    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        print("📧 Email sent via SendGrid!")

    except Exception as e:
        print("❌ SendGrid error:", e)