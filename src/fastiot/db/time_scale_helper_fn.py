
# --------- apt-get install libpq-dev first to install psycopg2 !!! -----------
import logging
import sys
import time

from fastiot.env.env import env_timescaledb
from fastiot.exceptions import ServiceError


def open_timescaledb_connection_from_env():
    db_connection = open_timescaledb_connection(
        host=env_timescaledb.host,
        port=env_timescaledb.port,
        user=env_timescaledb.user,
        password=env_timescaledb.password,
        database=env_timescaledb.database
    )
    return db_connection


def open_timescaledb_connection(host: str, port: int, user: str, password: str,
                                database: str = None):

    try:
        # pylint: disable=import-outside-toplevel
        import psycopg2
        from psycopg2 import OperationalError
    except (ImportError, ModuleNotFoundError):
        logging.error("You have to manually install `psycopg2>=2.9.3,<3` using your `requirements.txt` "
                      "to make use of this helper.")
        sys.exit(5)

    connection_parameters = {"user": user, "password": password, "host": host,
                             "port": port, "database": database}

    # We found that the postgres connection with docker sometimes failed, because of the env variables in
    # docker-compose.yaml are not really set. Try docker-compose up -d --force-recreate to start the test environment.
    sleep_time = 0.2
    num_tries = 300 / sleep_time
    while num_tries > 0:
        try:
            db_connection = psycopg2.connect(**connection_parameters)
            return db_connection
        except OperationalError:
            time.sleep(sleep_time)
        num_tries -= 1
    raise ServiceError("Could not connect to TimeScaleDB")
