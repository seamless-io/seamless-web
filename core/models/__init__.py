import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


_base = None


def _get_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


_session = None


def get_session():
    global _session
    if not _session:
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', 'root')
        host = os.getenv('DB_HOST', '127.0.0.1')
        port = os.getenv('DB_PORT', 5432)
        db_name = os.getenv('DB_NAME', 'seamless')
        sqlalchemy_url = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}'
        # it seems like we do not need it
        # ca_cert_file = os.path.join(
        #     os.path.realpath(os.path.dirname(__file__)),
        #     'rds-ca-2019-root.pem'
        # )
        # sqlalchemy_url += '?sslmode=verify-full&sslrootcert={}'.format(ca_cert_file)
        # no point to have more then 1 connection since we are not doing threads
        engine = create_engine(sqlalchemy_url, pool_size=1, max_overflow=2, pool_pre_ping=True)
        _session = _get_session(engine)
    return _session


@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.
    https://docs.sqlalchemy.org/en/13/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it
    """
    session = get_session(get_engine())
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
