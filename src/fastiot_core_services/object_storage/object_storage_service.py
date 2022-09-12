import logging
from typing import Any

import pymongo
from pydantic import BaseModel
from pymongo.collection import Collection

from fastiot.core.service_annotations import subscribe
from fastiot.core import FastIoTService, Subject
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.env import env_mongodb, env_mongodb_cols
from fastiot.helpers.read_yaml import read_config
from fastiot.msg.thing import Thing
from fastiot_core_services.object_storage.env import env_object_storage
from fastiot_core_services.object_storage.object_storage_fn import convert_message_to_mongo_data


class ObjectStorageService(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mongo_client = get_mongodb_client_from_env()
        database = self._mongo_client.get_database(env_mongodb.name)
        self._mongo_object_db_col = database.get_collection(env_mongodb_cols.object_storage)

        service_config = read_config(self)

        mongo_indicies = service_config['mongodb']['search_index']
        for index_name in mongo_indicies:
            self._mongo_client.create_index(collection=self._mongo_object_db_col,
                                            index=[(index_name, pymongo.ASCENDING)],
                                            index_name=f"{index_name}_ascending")

    async def _start(self):
        pass

    async def _stop(self):
        pass

    @subscribe(subject=Subject(name=env_object_storage.subject, msg_cls=dict))
    async def _cb_receive_primitive_data(self, subject_name: str, msg: Any):
        logging.info("Received message %s" % (str(msg)))
        mongo_data = convert_message_to_mongo_data(msg)
        logging.info("Converted Mongo data is ", mongo_data)
        self._mongo_object_db_col.insert_one(mongo_data)

