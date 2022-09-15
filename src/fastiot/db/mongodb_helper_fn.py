import logging
import sys
from typing import Dict, List, Tuple, Union, Any

from pymongo.collection import Collection

from fastiot.env import env_mongodb
from fastiot.exceptions import ServiceError
from fastiot.msg.time_series_msg import TimeSeriesData


class CustomMongoClient:
    def __init__(self, db_host: str, db_port: int, db_user: str = None, db_password: str = None,
                 db_auth_source: str = None, db_compression: str = None):
        """
        Constructor for a customer mongo client. Please note, that it will also set the feature compatibility version to
        the current mongodb version which may cause the database to be harder to downgrade.

        *Note:* You have to manually install ``pymongo>=4.1,<5`` using your :file:`requirements.txt` to make use of this
        helper. Database clients are not automatically installed to keep the containers smaller.
        """
        try:
            # pylint: disable=import-outside-toplevel
            from bson.binary import UUID_SUBTYPE
            from bson.codec_options import CodecOptions
            from pymongo import MongoClient
            from pymongo.errors import ConnectionFailure
        except (ImportError, ModuleNotFoundError):
            logging.error("You have to manually install `pymongo>=4.1,<5` using your `requirements.txt` to make use of "
                          "this helper.")
            sys.exit(5)

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
            self._db_client.admin.command('ping')
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

    def health_check(self) -> bool:
        connected_nodes = self._db_client.nodes
        if connected_nodes is not None:
            return True
        return False

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

    @staticmethod
    def create_index(collection: Collection, index: List[Tuple[str, Union[int, Any]]], index_name: str) -> bool:
        """
        Creates the defined index in the defined collection if the index does not exist.
        Otherwise no changes will be done to the database to save time consuming rebuilding of the index

        :param collection: Collection (instance, not name) to create index in
        :param index: Define index as wanted by pymongo create_index, eg. [(column_name, pymongo.ASCENDING)]
        Instead of pymongo.ASCENDING you can also write 1, DESCENDING is -1
        :param index_name: Define a unique name for the index. This name will be used to check if index has already been
        created

        return True if index was created, False if index has been created already
        """
        all_indices = [index['name'] for index in collection.list_indexes()]
        if index_name not in all_indices:
            collection.create_index(index, name=index_name)
            logging.getLogger("mongodb_helper_fn").info("Created new MongoDB index %s", index_name)
            return True

        return False

    def close(self):
        self._db_client.close()


def get_mongodb_client_from_env() -> CustomMongoClient:
    """
    For connecting Mongodb, the environment variables can be set,
    if you want to use your own settings instead of default:
    FASTIOT_MONGO_DB_HOST, FASTIOT_MONGO_DB_PORT, FASTIOT_MONGO_DB_USER, FASTIOT_MONGO_DB_PASSWORD,
    FASTIOT_MONGO_DB_AUTH_SOURCE, FASTIOT_MONGO_DB_NAME

    >>> mongo_client = get_mongodb_client_from_env()
    """
    db_client = CustomMongoClient(
        db_host=env_mongodb.host,
        db_port=env_mongodb.port,
        db_user=env_mongodb.user,
        db_password=env_mongodb.password,
        db_auth_source=env_mongodb.auth_source
    )
    return db_client


def time_series_data_to_mongodb_data_set(time_series_data: TimeSeriesData) -> Dict:
    data_set = {
        '_id': time_series_data.id,
        'name': time_series_data.name,
        'service_id': time_series_data.service_id,
        'measurement_id': time_series_data.measurement_id,
        'dt_start': time_series_data.dt_start,
        'dt_end': time_series_data.dt_end,
        'modified_at': time_series_data.modified_at,
        'values': time_series_data.values
    }
    return data_set


def time_series_data_from_mongodb_data_set(data_set: Dict) -> TimeSeriesData:
    time_series_data = TimeSeriesData(
        id=data_set['_id'],
        name=data_set['name'],
        service_id=data_set['service_id'],
        measurement_id=data_set['measurement_id'],
        dt_start=data_set['dt_start'],
        dt_end=data_set['dt_end'],
        modified_at=data_set['modified_at'],
        values=data_set['value']
    )
    return time_series_data

