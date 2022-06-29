import logging

from bson.binary import UUID_SUBTYPE
from bson.codec_options import CodecOptions
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from fastiot.env.env import env_mongodb
from fastiot.exceptions.exceptions import ServiceError


class CustomMongoClient:
    def __init__(self, db_host: str, db_port: int, db_user: str = None, db_password: str = None,
                 db_auth_source: str = None, db_compression: str = None):
        """
        Constructor for a customer mongo client. Please note, that it will also set the feature compatibility version to
        the current mongodb version which may cause the database to be harder to downgrade.
        """
        mongo_client_kwargs = {
            "host": db_host,
            "port": db_port,
            "username": db_user,
            "password": db_password
        }

        if db_auth_source is not None:
            mongo_client_kwargs["authSource"] = db_auth_source

        if db_compression is not None:
            mongo_client_kwargs["compressors"] = db_compression
            if db_compression == "zlib":
                mongo_client_kwargs["zlibCompressionLevel"] = 9

        self._db_client = MongoClient(**mongo_client_kwargs)

        try:
            self._db_client.admin.command('ismaster')
            logging.getLogger("mongodb_helper_fn").info("Connection to database established")
        except ConnectionFailure:
            logging.getLogger("mongodb_helper_fn").exception("Connecting to database failed")
            raise ServiceError("Database is not available")

        self.__set_version_compatibility_to_current_version()
        self._codec_options = CodecOptions(uuid_representation=UUID_SUBTYPE)

    def __set_version_compatibility_to_current_version(self):
        version_array = self._db_client.server_info()['versionArray']
        version = f"{version_array[0]}.{version_array[1]}"
        self._db_client.admin.command({"setFeatureCompatibilityVersion": version})

    def get_database(self, name):
        if name is None:
            raise ValueError('database name is None, please assign a value')
        return self._db_client.get_database(name, codec_options=self._codec_options)

    def drop_datebase(self, name):
        if name is None:
            raise ValueError('database name is None, please assign a value')
        self._db_client.drop_database(name)

    def fsync(self):
        self._db_client.admin.command('fsync', lock=True)


def get_mongodb_client_from_env() -> CustomMongoClient:
    db_client = CustomMongoClient(
        db_host=env_mongodb.host,
        db_port=env_mongodb.port,
        db_user=env_mongodb.user,
        db_password=env_mongodb.password,
        db_auth_source=env_mongodb.auth_source
    )
    return db_client

