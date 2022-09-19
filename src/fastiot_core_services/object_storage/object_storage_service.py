from datetime import datetime
from typing import List, Dict

import pymongo

from fastiot import logging
from fastiot.core import FastIoTService, Subject
from fastiot.core.data_models import ReplySubject
from fastiot.core.service_annotations import subscribe, reply
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.env import env_mongodb, env_mongodb_cols
from fastiot.helpers.read_yaml import read_config
from fastiot.msg.hist import HistObjectReq, HistObjectResp
from fastiot_core_services.object_storage.env import env_object_storage


class ObjectStorageService(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logger = logging('object_storage')
        self._mongo_client = get_mongodb_client_from_env()
        database = self._mongo_client.get_database(env_mongodb.name)
        self._mongo_object_db_col = database.get_collection(env_mongodb_cols.object_storage)
        service_config = read_config(self)

        mongo_indicies = service_config['mongodb']['search_index']
        for index_name in mongo_indicies:
            self._mongo_client.create_index(collection=self._mongo_object_db_col,
                                            index=[(index_name, pymongo.ASCENDING)],
                                            index_name=f"{index_name}_ascending")

    @subscribe(subject=Subject(name=env_object_storage.subject, msg_cls=dict))
    async def _cb_receive_data(self, subject_name: str, msg: dict):
        self._logger.debug("Received message %s", str(msg))
        if 'timestamp' in list(msg.keys()):
            timestamp = msg['timestamp']
        else:
            timestamp = datetime.utcnow()
        mongo_data = {'_timestamp': timestamp, '_subject': subject_name, 'Object': msg}
        self._logger.debug("Converted Mongo data is %s" % mongo_data)
        self._mongo_object_db_col.insert_one(mongo_data)

    @reply(ReplySubject(name="reply_object",
                        msg_cls=HistObjectReq,
                        reply_cls=HistObjectResp))
    async def reply_hist_object(self, subject: str, hist_object_req: HistObjectReq) -> HistObjectResp:
        self._logger.debug("Received request on subject %s with message %s", subject, hist_object_req)
        query_dict = {"_timestamp": {'$gte': hist_object_req.dt_start, '$lte': hist_object_req.dt_end}}
        query_results = self._query_db(query_dict=query_dict)
        values = [result['Object'] for result in query_results]
        hist_object_resp = HistObjectResp(machine=hist_object_req.machine,
                                          name=hist_object_req.name,
                                          values=values)
        return hist_object_resp

    def _query_db(self, query_dict: Dict) -> List:
        return list(self._mongo_object_db_col.find(query_dict))
