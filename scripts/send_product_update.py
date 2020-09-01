from time import sleep

from dotenv import load_dotenv

from core.emails.client import send_email
from core.models import get_db_session, User

load_dotenv()

users = get_db_session().query(User).all()

with open('<name of html file with update>', 'r') as file:
    content = file.read()
for user in users:
    print(user.email)
    send_email(user.email,
               'Seamless Cloud Product Update <date>',
               content)
    sleep(1)

