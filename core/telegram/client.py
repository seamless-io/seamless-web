import logging
from datetime import datetime, timedelta

import requests
from sentry_sdk import capture_exception

from config import TELEGRAM_BOT_API_KEY, TELEGRAM_CHANNEL_ID
from core.models import get_db_session, User, Job, JobRun


def _send_message(message):
    resp = requests.get(f'https://api.telegram.org/bot{TELEGRAM_BOT_API_KEY}/sendMessage',
                        params={'chat_id': TELEGRAM_CHANNEL_ID,
                                'text': message})
    try:
        resp.raise_for_status()
    except Exception as e:
        logging.error(e)
        capture_exception(e)


def notify_about_new_user(email):
    _send_message(f"Fuck yeah, new user {email}")


def send_daily_stats():
    day_ago = datetime.utcnow() - timedelta(days=1)
    new_registrations = get_db_session().query(User).filter(User.created_at >= day_ago).count()
    new_jobs = get_db_session().query(Job).filter(Job.created_at >= day_ago).count()
    new_job_runs = get_db_session().query(JobRun).filter(JobRun.created_at >= day_ago).count()
    _send_message(f"Last 24h update:\n"
                  f"{new_registrations} registrations\n"
                  f"{new_jobs} Jobs published\n"
                  f"{new_job_runs} Job Runs (run button + scheduled)")