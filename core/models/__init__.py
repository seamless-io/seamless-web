import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_PREFIX = 'SEAMLESS'
EXISTING_DB = ('SEAMLESS', 'INTEGRATION_TEST')


def get_sqlalchemy_url(db_prefix):
    sqlalchemy_url = '{db}+{conn}://{user}:{password}@{host}:{port}/{db_name}'

    db_vars = {
        'db': os.getenv(f'{db_prefix}_DB', 'postgresql'),
        'conn': os.getenv(f'{db_prefix}_DB_CONNECTOR', 'psycopg2'),
        'user': os.getenv(f'{db_prefix}_DB_USER', 'postgres'),
        'password': os.getenv(f'{db_prefix}_DB_PASSWORD', 'root'),
        'host': os.getenv(f'{db_prefix}_DB_HOST', 'postgres'),
        'port': os.getenv(f'{db_prefix}_DB_PORT', 5432),
        'db_name': os.getenv(f'{db_prefix}_DB_NAME', 'seamless')
    }
    url = sqlalchemy_url.format(**db_vars)
    if os.getenv('DB_USE_SSL', False):
        ca_cert_file = os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            'rds-combined-ca-bundle.pem'
        )
        url += '?sslmode=verify-full&sslrootcert={}'.format(ca_cert_file)
    return url


def _get_engine(db_prefix):
    if db_prefix not in EXISTING_DB:
        error_msg = 'Database prefix can be one of: {}'
        raise KeyError(error_msg.format(', '.join(EXISTING_DB)))
    return create_engine(get_sqlalchemy_url(db_prefix))


def get_session_factory(db_prefix=DB_PREFIX):
    return sessionmaker(bind=_get_engine(db_prefix))
