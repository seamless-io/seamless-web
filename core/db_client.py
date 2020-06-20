import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

EXISTING_DB = ('SEAMLESS', 'SEAMLESS_PASSWORDS', 'SEAMLESS_TEST')

_base = None


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
    return create_engine(
        get_sqlalchemy_url(db_prefix),
        # no point to have more then 1 connection since we are not doing
        # threads
        pool_size=1,
        max_overflow=2,
        pool_pre_ping=True,
    )


def _get_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


_engine = None


def get_engine():
    global _engine
    if not _engine:
        _engine = _get_engine('SEAMLESS')
    return _engine


_session = None


def get_session():
    global _session
    if not _session:
        _session = _get_session(get_engine())
    return _session


@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.
    https://docs.sqlalchemy.org/en/13/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it
    """
    session = _get_session(get_engine())
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
