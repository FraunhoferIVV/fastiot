""" Module to hold basic environment variables """

from fastiot.env.env_basic import BasicEnv, TestsEnv
from fastiot.env.env_broker import BrokerEnv
from fastiot.env.env_influxdb import InfluxDBEnv
from fastiot.env.env_mariadb import MariaDBEnv
from fastiot.env.env_mongodb import MongoDBEnv, MongoDBColConstants
from fastiot.env.env_redis import RedisEnv
from fastiot.env.env_timescaledb import TimeScaleDBEnv

env_basic = BasicEnv()
env_tests = TestsEnv()
env_broker = BrokerEnv()
env_mongodb = MongoDBEnv()
env_mongodb_cols = MongoDBColConstants()
env_mariadb = MariaDBEnv()
env_influxdb = InfluxDBEnv()
env_timescaledb = TimeScaleDBEnv()
env_redis = RedisEnv()
