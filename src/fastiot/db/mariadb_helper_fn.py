import logging
import sys
import time

from typing import List, Tuple, Optional

from fastiot.env.env import env_mariadb
from fastiot.exceptions.exceptions import ServiceError


def open_mariadb_connection_from_env(schema: Optional[str] = None):
    """
    Establishes a connection to a MariaDB instance and returns a Connection object.

    An optional schema name can be specified. The connection should be closed before termination.
    """
    db_connection = open_mariadb_connection(
        host=env_mariadb.host,
        port=env_mariadb.port,
        schema=schema,
        user=env_mariadb.user,
        password=env_mariadb.password
    )
    return db_connection


def open_mariadb_connection(host: str, port: int, schema: Optional[str],
                            user: str, password: str):
    # We found that mariadb initial start time takes very long in some environments. Therefore we need a timeout much
    # greater then two minutes.
    try:
        # pylint: disable=import-outside-toplevel
        import pymysql.cursors
    except (ImportError, ModuleNotFoundError):
        logging.error("You have to manually install `PyMySQL>=1.0,<2` using your `requirements.txt` "
                      "to make use of this helper.")
        sys.exit(5)

    sleep_time = 0.2
    num_tries = 300 / sleep_time
    while num_tries > 0:
        try:
            db_connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=schema,
                cursorclass=pymysql.cursors.DictCursor
            )
            return db_connection
        except pymysql.err.OperationalError:
            time.sleep(sleep_time)
        num_tries -= 1
    raise ServiceError("Could not connect to MariaDB")
