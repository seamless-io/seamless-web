from time import sleep

from dotenv import load_dotenv

from core.emails.client import send_email
from core.models import get_db_session, User

unsubscribed_list = ['ctapbiu.spb@gmail.com',
                     'hubermar4@gmail.com',
                     'sktplogzlboyrqptlp@twzhhq.online']

load_dotenv()

users = get_db_session().query(User).all()

with open('path to email template', 'r') as file:
    content = file.read()
for user in users:
    if user.email not in unsubscribed_list:
        print(user.email)
        send_email(user.email,
                   'Seamless Cloud Product Update 09-26-2020',
                   content)
        sleep(1)
