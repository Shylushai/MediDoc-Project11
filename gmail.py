import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_email(sender_email, receiver_email, subject, body):
    """
    Creates the email content.

    Args:
        sender_email (str): The sender's email address.
        receiver_email (str): The receiver's email address.
        subject (str): The email subject.
        body (str): The email body.

    Returns:
        MIMEMultipart: The composed email message.
    """
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    return message


def send_gmail_notification(sender_email, receiver_email, app_password, subject, body):
    """
    Sends a Gmail notification.

    Args:
        sender_email (str): The sender's email address.
        receiver_email (str): The receiver's email address.
        app_password (str): The app password for the sender's Gmail account.
        subject (str): The email subject.
        body (str): The email body.
    """
    try:
        # Create a secure SSL context
        context = ssl.create_default_context()

        # Set up the server and send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, app_password)

            # Create the email content
            message = create_email(sender_email, receiver_email, subject, body)

            # Send the email
            server.sendmail(sender_email, receiver_email, message.as_string())
            logging.info("Email sent successfully to %s", receiver_email)

    except smtplib.SMTPException as e:
        logging.error("Failed to send email: %s", e)
    except Exception as e:
        logging.error("An error occurred: %s", e)
