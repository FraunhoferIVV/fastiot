import sys
import time

from fastiot import logging
from fastiot.env.env import env_timescaledb
from fastiot.exceptions import ServiceError


def get_timescaledb_client_from_env():
    """
    For connecting TimeScaleDB, the environment variables can be set,
    if you want to use your own settings instead of default:
    :envvar:`FASTIOT_TIME_SCALE_DB_HOST`, :envvar:`FASTIOT_TIME_SCALE_DB_PORT`, :envvar:`FASTIOT_TIME_SCALE_DB_USER`,
    :envvar:`FASTIOT_TIME_SCALE_DB_PASSWORD`, :envvar:`FASTIOT_TIME_SCALE_DB_DATABASE`

    *Attention*: You must have `libpq-dev` installed in your system (or your container), e.g.
    :command:`apt-get install libpq-dev`.

    >>> time_scale_db_client = get_timescaledb_client_from_env()
    """
    db_client = get_timescaledb_client(
        host=env_timescaledb.host,
        port=env_timescaledb.port,
        user=env_timescaledb.user,
        password=env_timescaledb.password,
        database=env_timescaledb.database
    )
    return db_client


def get_timescaledb_client(host: str, port: int, user: str, password: str,
                           database: str = None):
    try:
        # pylint: disable=import-outside-toplevel
        import psycopg2
        from psycopg2 import OperationalError
    except (ImportError, ModuleNotFoundError):
        logging.error("You have to manually install `fastiot[postgredb]` or `psycopg2>=2.9.3,<3` using your "
                      "`pyproject.toml` to make use of this helper.")
        sys.exit(5)

    client_parameters = {"user": user, "password": password, "host": host,
                         "port": port, "database": database}

    # We found that the postgres connection with docker sometimes failed, because of the env variables in
    # docker-compose.yaml are not really set. Try docker-compose up -d --force-recreate to start the test environment.
    sleep_time = 0.2
    num_tries = 300 / sleep_time
    while num_tries > 0:
        try:
            db_client = psycopg2.connect(**client_parameters)
            return db_client
        except OperationalError:
            time.sleep(sleep_time)
        num_tries -= 1
    raise ServiceError("Could not connect to TimeScaleDB")
