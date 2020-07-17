import os

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
