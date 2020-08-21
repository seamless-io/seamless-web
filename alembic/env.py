import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from core.models.base import base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_sqlalchemy_url(db_prefix):
    sqlalchemy_url = '{db}+{conn}://{user}:{password}@{host}:{port}/{db_name}'

    db_vars = {
        'db': os.getenv(f'{db_prefix}_DB', 'postgresql'),
        'conn': os.getenv(f'{db_prefix}_DB_CONNECTOR', 'psycopg2'),
        'user': os.getenv(f'{db_prefix}_DB_USER', 'postgres'),
        'password': os.getenv(f'{db_prefix}_DB_PASSWORD', 'root'),
        'port': os.getenv(f'{db_prefix}_DB_PORT', 5432),
        'db_name': os.getenv(f'{db_prefix}_DB_NAME', 'seamless'),

        # This function is only used for `make setup-db`
        # which always uses a postgres instance launched in a docker container
        'host': 'postgres',
    }
    url = sqlalchemy_url.format(**db_vars)
    if os.getenv('DB_USE_SSL', False):
        ca_cert_file = os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            'rds-combined-ca-bundle.pem'
        )
        url += '?sslmode=verify-full&sslrootcert={}'.format(ca_cert_file)
    return url


def run_migrations_offline():
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            transaction_per_migration=True,
            compare_type=True,
            include_schemas=True
        )

        with context.begin_transaction():
            # context.execute('SET search_path TO public')
            context.run_migrations()


def run():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()


if __name__ == 'env_py':
    config.set_main_option('sqlalchemy.url', get_sqlalchemy_url('SEAMLESS'))
    run()
