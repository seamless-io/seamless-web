from datetime import datetime
from time import sleep

from dotenv import load_dotenv

from core.emails.client import send_email
from core.models import get_db_session, User

unsubscribed_list = ['ctapbiu.spb@gmail.com',
                     'hubermar4@gmail.com',
                     'sktplogzlboyrqptlp@twzhhq.online',
                     'guyheidemann@gmail.con']

load_dotenv()

users = get_db_session().query(User).filter(User.created_at > datetime(2020, 9, 27),
                                            User.created_at < datetime(2020, 10, 2)).all()

with open('ask_for_feedback.html', 'r') as file:
    content = file.read()
for user in users:
    if user.email not in unsubscribed_list:
        print(user.email)
        send_email(user.email,
                   'I need your advice to improve the product',
                   content)
        sleep(5)
