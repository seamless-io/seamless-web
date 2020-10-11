import enum
import os
import smtplib
from email.message import EmailMessage

import constants


class EmailFromType(enum.Enum):
    PERSONAL = 'Andrey <andrey@seamlesscloud.io>'
    TRANSACTIONAL = 'Seamless Cloud Notifications <notifications@seamlesscloud.io>'


def send_email(email_from_type: EmailFromType, recipient: str, subject: str, body: str):
    msg = EmailMessage()
    msg['From'] = email_from_type.value
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(body, subtype='html')

    with smtplib.SMTP('smtp.gmail.com', port=587) as smtp_server:
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.login(constants.PERSONAL_EMAIL_SENDER,
                          os.getenv('EMAIL_AUTOMATION_PASSWORD'))
        smtp_server.send_message(msg)


def send_welcome_email(recipient):
    with open('core/emails/welcome.html', 'r') as file:
        send_email(recipient,
                   'Welcome to Seamless Cloud community',
                   file.read())
