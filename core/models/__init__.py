import os

from flask import has_app_context
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .users import User
from .jobs import Job
from .job_runs import JobRun
from .job_run_logs import JobRunLog
from .job_parameters import JobParameter
from .job_templates import JobTemplate
from .workspaces import Workspace
from .users_workspaces import UserWorkspace

DB_PREFIX = 'SEAMLESS'
EXISTING_DB = ('SEAMLESS', 'INTEGRATION_TEST')

flask_db_session = None
non_flask_db_session = None


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


def get_db_session():
    if has_app_context():
        # This branch is used when we're working in the scope of Flask app
        global flask_db_session
        if not flask_db_session:
            from application import application
            flask_db_session = flask_scoped_session(get_session_factory(), application)
        return flask_db_session
    else:
        # We use a different session if we're outside of Flask app,
        # for example running our code in a separate Thread
        global non_flask_db_session
        if not non_flask_db_session:
            non_flask_db_session = scoped_session(get_session_factory(DB_PREFIX))()
        return non_flask_db_session


def db_commit():
    """
    https://stackoverflow.com/questions/8870217/why-do-i-get-sqlalchemy-nested-rollback-error
    """
    try:
        get_db_session().commit()
    except Exception as e:
        get_db_session().rollback()
        raise e
