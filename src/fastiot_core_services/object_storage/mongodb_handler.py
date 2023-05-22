from datetime import timezone
from typing import List, Tuple, Union, Any

from bson.binary import UUID_SUBTYPE
from bson.codec_options import CodecOptions
from pymongo.collection import Collection

from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env


class MongoDBHandler:
    def __init__(self):
        self._db_client = get_mongodb_client_from_env()

    def health_check(self) -> bool:
        connected_nodes = self._db_client.nodes
        if connected_nodes is not None:
            return True
        return False

    def get_database(self, name):
        if name is None:
            raise ValueError('database name is None, please assign a value')
        return self._db_client.get_database(name,
                                            codec_options=CodecOptions(uuid_representation=UUID_SUBTYPE,
                                                                       tz_aware=True, tzinfo=timezone.utc))

    def drop_database(self, name):
        if name is None:
            raise ValueError('database name is None, please assign a value')
        self._db_client.drop_database(name)

    def fsync(self):
        self._db_client.admin.command('fsync', lock=True)

    @staticmethod
    def create_index(collection: Collection, index: List[Tuple[str, Union[int, Any]]], index_name: str) -> bool:
        """
        Creates the defined index in the defined collection if the index does not exist.
        Otherwise, no changes will be done to the database to save time-consuming rebuilding of the index

        :param collection: Collection (instance, not name) to create index in
        :param index: Define index as wanted by pymongo create_index, eg. [(column_name, pymongo.ASCENDING)]
                      Instead of pymongo.ASCENDING you can also write 1, DESCENDING is -1
        :param index_name: Define a unique name for the index. This name will be used to check if index has already been
                           created
        :returns: True if index has been created, False if index has been created already

        """
        all_indices = [index['name'] for index in collection.list_indexes()]
        if index_name not in all_indices:
            collection.create_index(index, name=index_name)
            return True

        return False

    def close(self):
        self._db_client.close()
