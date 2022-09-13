import logging
from typing import Any, List, Dict

import pymongo
from pydantic import BaseModel
from pymongo.collection import Collection

from fastiot.core.service_annotations import subscribe, reply
from fastiot.core import FastIoTService, Subject
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.env import env_mongodb, env_mongodb_cols
from fastiot.helpers.read_yaml import read_config
from fastiot.msg.hist import HistThingReq, HistThingResp
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

    @reply(Subject(name="reply_thing",
                   msg_cls=HistThingReq,
                   reply_cls=HistThingResp))
    async def reply_hist_thing(self, subject: str, hist_thing_req: HistThingReq) -> HistThingResp:
        print("Received request on subject %s with message %s" %(subject, hist_thing_req))
        query_dict = {"timestamp": {'$gte': hist_thing_req.dt_start, '$lte': hist_thing_req.dt_end},
                      "Object.machine": hist_thing_req.machine,
                      "Object.name": hist_thing_req.name}
        query_results = self._query_db(query_dict=query_dict)
        values = [Thing.parse_obj(result['Object']) for result in query_results]
        hist_thing_resp = HistThingResp(machine=hist_thing_req.machine,
                                        name=hist_thing_req.name,
                                        values=values)
        return hist_thing_resp


    def _query_db(self, query_dict: Dict) -> List:
        return list(self._mongo_object_db_col.find(query_dict))
