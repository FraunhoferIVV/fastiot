import os

from fastiot.env.env_constants import *


FASTIOT_TEST_ENVIRONMENT = {
    FASTIOT_MONGO_DB_HOST: "localhost",
    FASTIOT_MONGO_DB_PORT: "17017",
    FASTIOT_MONGO_DB_USER: "root",
    FASTIOT_MONGO_DB_PASSWORD: "ADFvs33fFAf3#FDfe3fdve3-df",
    FASTIOT_MONGO_DB_AUTH_SOURCE: "admin",
    FASTIOT_MARIA_DB_HOST: "127.0.0.1",
    FASTIOT_MARIA_DB_PORT: "3307",
    FASTIOT_MARIA_DB_USER: "root",
    FASTIOT_MARIA_DB_PASSWORD: "ADFvs33fFAf3#FDfe3fdve3-df",
    FASTIOT_MARIA_DB_SCHEMA_FASTIOTLIB: "fastiot_fastiotlib",
    FASTIOT_INFLUX_DB_HOST: "localhost",
    FASTIOT_INFLUX_DB_PORT: "8087",
    FASTIOT_INFLUX_DB_TOKEN: "ndExs0Yws4zBCtBs",
    FASTIOT_TIME_SCALE_DB_HOST: "localhost",
    FASTIOT_TIME_SCALE_DB_PORT: "54332",
    FASTIOT_TIME_SCALE_DB_USER: "postgres",
    FASTIOT_TIME_SCALE_DB_PASSWORD: "ADFvs33fFAf3#FDfe3fdve3-df",
    FASTIOT_TIME_SCALE_DB_DATABASE: "fastiot_db"
}


def populate_db_test_env():
    for test_env in FASTIOT_TEST_ENVIRONMENT:
        os.environ[test_env] = FASTIOT_TEST_ENVIRONMENT[test_env]
