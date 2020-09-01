import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

AUTH0_BASE_URL = os.getenv('AUTH0_BASE_URL')
AUTH0_WEB_API_AUDIENCE = os.getenv('AUTH0_WEB_API_AUDIENCE')
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
AUTH0_CALLBACK_URL = os.getenv('AUTH0_CALLBACK_URL')
LAMBDA_PROXY_PASSWORD = os.getenv('LAMBDA_PROXY_PASSWORD')
LAMBDA_PROXY_NAME = os.getenv('LAMBDA_PROXY_NAME')
LAMBDA_PROXY_ARN = os.getenv('LAMBDA_PROXY_ARN')
SENTRY_DSN = os.getenv('SENTRY_DSN')
STAGE = os.getenv('STAGE', 'local')
TELEGRAM_BOT_API_KEY = os.getenv('TELEGRAM_BOT_API_KEY')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
EMAIL_AUTOMATION_PASSWORD = os.getenv('EMAIL_AUTOMATION_PASSWORD')
GITHUB_ACTIONS_PASSWORD = os.getenv('GITHUB_ACTIONS_PASSWORD')
EMAIL_AUTOMATION_SENDER = 'andrey@seamlesscloud.io'
DEFAULT_ENTRYPOINT = 'function.py'
DEFAULT_REQUIREMENTS = 'requirements.txt'
DEFAULT_CRON_SCHEDULE = "0 0 * * *"
