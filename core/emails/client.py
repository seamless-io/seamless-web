import os
import smtplib
from email.message import EmailMessage

import constants


def send_email(recipient, subject, body):
    msg = EmailMessage()
    msg['From'] = constants.EMAIL_AUTOMATION_SENDER
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(body, subtype='html')

    with smtplib.SMTP('smtp.gmail.com', port=587) as smtp_server:
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.login(constants.EMAIL_AUTOMATION_SENDER,
                          os.getenv('EMAIL_AUTOMATION_PASSWORD'))
        smtp_server.send_message(msg)


def send_welcome_email(recipient):
    with open('core/emails/welcome.html', 'r') as file:
        send_email(recipient,
                   'Welcome to Seamless Cloud',
                   file.read())
