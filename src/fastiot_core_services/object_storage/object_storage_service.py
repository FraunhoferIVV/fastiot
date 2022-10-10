from datetime import datetime
from typing import List, Dict

import pymongo

from fastiot import logging
from fastiot.core import FastIoTService, Subject
from fastiot.core.service_annotations import reply
from fastiot.core.subject_helper import sanitize_subject_name
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.env import env_mongodb, env_mongodb_cols
from fastiot.util.read_yaml import read_config
from fastiot.msg.hist import HistObjectReq, HistObjectResp
from fastiot_core_services.object_storage.mongodb_handler import MongoDBHandler
from fastiot_core_services.object_storage.object_storage_helper_fn import to_mongo_data, build_query_dict, \
    from_mongo_data, get_collection_name


class ObjectStorageService(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        service_config = read_config(self)

        self._mongodb_handler = MongoDBHandler()

        database = self._mongodb_handler.get_database(env_mongodb.name)
        self._mongo_object_db_col = database.get_collection(get_collection_name(service_config['subject_name']))
        mongo_indices = service_config['search_index']
        for index_name in mongo_indices:
            self._mongodb_handler.create_index(collection=self._mongo_object_db_col,
                                               index=[(index_name, pymongo.ASCENDING)],
                                               index_name=f"{index_name}_ascending")
        self.subject = Subject(name=sanitize_subject_name(service_config['subject_name']), msg_cls=dict)
        self.reply_subject = HistObjectReq.get_reply_subject(name=service_config['subject_name'],
                                                             reply_cls=HistObjectResp)

    async def _start(self):
        await self.broker_connection.subscribe(subject=self.subject, cb=self._cb_receive_data)
        await self.broker_connection.subscribe_reply_cb(subject=self.reply_subject, cb=self._cb_reply_hist_object)

    async def _cb_receive_data(self, subject_name: str, msg: dict):
        logging.debug("Received message %s", str(msg))
        if 'timestamp' in list(msg.keys()):
            timestamp = msg['timestamp']
        else:
            timestamp = datetime.utcnow()
        mongo_data = to_mongo_data(timestamp=timestamp, subject_name=subject_name, msg=msg)
        logging.debug("Converted Mongo data is %s", mongo_data)
        self._mongo_object_db_col.insert_one(mongo_data)

    async def _cb_reply_hist_object(self, subject: str, hist_object_req: HistObjectReq) -> HistObjectResp:
        logging.debug("Received request on subject %s with message %s", subject, hist_object_req)
        query_dict = build_query_dict(hist_object_req=hist_object_req)
        query_results = self._query_db(query_dict=query_dict, limit_nr=hist_object_req.limit)
        values = [from_mongo_data(result) for result in query_results]
        hist_object_resp = HistObjectResp(values=values)
        return hist_object_resp

    def _query_db(self, query_dict: Dict, limit_nr: int) -> List:
        return list(self._mongo_object_db_col.find(query_dict).limit(limit_nr))
