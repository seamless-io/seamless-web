import logging
import os
import smtplib
from email.message import EmailMessage


def create_email_message(recipient, subject, body):
    msg = EmailMessage()
    msg['From'] = f"Seamless Cloud team <hello@seamlesscloud.io>"
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(body, subtype='html')
    return msg


def send_email(recipient, subject, body):
    if os.getenv('STAGE') != 'staging':  # TODO Switch to production when we're done testing
        logging.info(f'[TEST MODE, NO REAL EMAIL] Sent {subject} email to {recipient}')
    else:
        msg = create_email_message(
            recipient=recipient,
            subject=subject,
            body=body
        )

        with smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', port=587) as smtp_server:
            smtp_server.ehlo()
            smtp_server.starttls()
            smtp_server.login(os.getenv('EMAIL_SMTP_USERNAME'), os.getenv('EMAIL_SMTP_PASSWORD'))
            smtp_server.send_message(msg)
        logging.info(f'Sent {subject} email to {recipient}')
