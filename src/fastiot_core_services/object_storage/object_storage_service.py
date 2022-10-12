from datetime import datetime
from typing import List, Dict

import pymongo

from fastiot.core import FastIoTService, Subject
from fastiot.core.subject_helper import sanitize_pub_subject_name, filter_specific_sign
from fastiot.env import env_mongodb
from fastiot.msg.hist import HistObjectReq, HistObjectResp
from fastiot.util.read_yaml import read_config
from fastiot_core_services.object_storage.mongodb_handler import MongoDBHandler
from fastiot_core_services.object_storage.object_storage_helper_fn import to_mongo_data, build_query_dict, \
    from_mongo_data, get_collection_name


class ObjectStorageService(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mongodb_handler = MongoDBHandler()
        database = self._mongodb_handler.get_database(env_mongodb.name)
        service_config = read_config(self)
        if not service_config:
            self._logger.warning('Please set the config as the same as in Documentation, to get over Errors.')

        self._mongo_object_db_col = database.get_collection(
            get_collection_name(service_config['collection'],
                                service_config['subject_name']))
        mongo_indices = service_config['search_index']
        for index_name in mongo_indices:
            self._mongodb_handler.create_index(collection=self._mongo_object_db_col,
                                               index=[(index_name, pymongo.ASCENDING)],
                                               index_name=f"{index_name}_ascending")
        self.subject = Subject(name=sanitize_pub_subject_name(service_config['subject_name']), msg_cls=dict)
        self.reply_subject = HistObjectReq.get_reply_subject(name=filter_specific_sign(service_config['subject_name']))

    async def _start(self):
        await self.broker_connection.subscribe(subject=self.subject, cb=self._cb_receive_data)
        await self.broker_connection.subscribe_reply_cb(subject=self.reply_subject, cb=self._cb_reply_hist_object)

    async def _cb_receive_data(self, subject_name: str, msg: dict):
        self._logger.debug("Received message %s", str(msg))
        if 'timestamp' in list(msg.keys()):
            timestamp = msg['timestamp']
        else:
            timestamp = datetime.utcnow()
        mongo_data = to_mongo_data(timestamp=timestamp, subject_name=subject_name, msg=msg)
        self._logger.debug("Converted Mongo data is %s", mongo_data)
        self._mongo_object_db_col.insert_one(mongo_data)

    async def _cb_reply_hist_object(self, subject: str, hist_object_req: HistObjectReq) -> HistObjectResp:
        self._logger.debug("Received request on subject %s with message %s", subject, hist_object_req)
        query_dict = build_query_dict(hist_object_req=hist_object_req)
        query_results = self._query_db(query_dict=query_dict, limit_nr=hist_object_req.limit)
        values = [from_mongo_data(result) for result in query_results]
        if values:
            hist_object_resp = HistObjectResp(values=values)
        else:
            hist_object_resp = HistObjectResp(
                error_msg='No query results from Mongodb, please check Connection or query',
                values=values)
        return hist_object_resp

    def _query_db(self, query_dict: Dict, limit_nr: int) -> List:
        return list(self._mongo_object_db_col.find(query_dict).limit(limit_nr))
