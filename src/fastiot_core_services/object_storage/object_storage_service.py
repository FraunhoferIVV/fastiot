import logging
import time
from datetime import datetime
from typing import List, Dict

import pymongo
from fastiot.core.time import get_time_now

from fastiot.core import FastIoTService, Subject
from fastiot.core.subject_helper import sanitize_pub_subject_name, filter_specific_sign
from fastiot.env import env_mongodb
from fastiot.msg.custom_db_data_type_conversion import to_mongo_data, from_mongo_data
from fastiot.msg.hist import HistObjectReq, HistObjectResp
from fastiot.util.read_yaml import read_config
from fastiot_core_services.object_storage.mongodb_handler import MongoDBHandler
from fastiot_core_services.object_storage.object_storage_helper_fn import build_query_dict


class ObjectStorageService(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mongodb_handler = MongoDBHandler()
        database = self._mongodb_handler.get_database(env_mongodb.name)
        service_config = read_config(self)
        if not service_config:
            self._logger.error('Please set the config as shown in the documentation! Aborting service!')
            time.sleep(10)
            raise RuntimeError

        self._mongo_object_db_col = database.get_collection(service_config['collection'])
        self._init_compound_index(service_config['search_index'])
        """
        mongo_indices = service_config['search_index']
        for index_name in mongo_indices:
            self._mongodb_handler.create_index(collection=self._mongo_object_db_col,
                                               index=[(index_name, pymongo.ASCENDING)],
                                               index_name=f"{index_name}_ascending")
        """
        self._enable_overwriting = ('enable_overwriting' in list(service_config.keys())
                                    and service_config['enable_overwriting'])
        if self._enable_overwriting:
            self._primary_keys = service_config['identify_object_with']

    def _init_compound_index(self, mongo_indices):
        compound_index = list(zip(mongo_indices,
                                  map(lambda index_name:
                                      pymongo.ASCENDING if index_name != '_timestamp'
                                      else pymongo.DESCENDING,
                                      mongo_indices)))
        # the later the _timestamp in mongo_data - the more time relevant query results
        self._logger.debug(compound_index)
        self._mongodb_handler.create_index(collection=self._mongo_object_db_col,
                                           index_name="compound_index",
                                           index=compound_index)

    async def _start(self):
        service_config = read_config(self)

        subject = Subject(name=sanitize_pub_subject_name(service_config['subject_name']), msg_cls=dict)
        await self.broker_connection.subscribe(subject=subject, cb=self._cb_receive_data)

        if not service_config.get('reply_subject_name'):
            self._logger.warning("Please set `reply_subject_name` in your configuration.\n"
                                 "Using `subject_name` for receiving and sending is deprecating.")
            service_config['reply_subject_name'] = service_config['subject_name']

        reply_subject = HistObjectReq.get_reply_subject(name=filter_specific_sign(service_config['subject_name']))
        await self.broker_connection.subscribe_reply_cb(subject=reply_subject, cb=self._cb_reply_hist_object)

    async def _cb_receive_data(self, subject_name: str, msg: dict):
        self._logger.debug("Received message %s", str(msg))
        # True for things; Possibly False for other messages
        if 'timestamp' in list(msg.keys()):
            timestamp = msg['timestamp']
        else:
            timestamp = get_time_now()
        mongo_data = to_mongo_data(timestamp=timestamp, subject_name=subject_name, msg=msg)
        self._logger.debug("Converted Mongo data is %s", mongo_data)
        if not self._enable_overwriting:
            self._mongo_object_db_col.insert_one(mongo_data)
        else:
            # the last overwriting data should be saved (overwriting has to be asynchron)
            await self._overwrite_data(mongo_data)

    async def _overwrite_data(self, mongo_data):
        # generate upsert query
        query = {}
        for key_name in self._primary_keys:
            query[key_name] = mongo_data[key_name]
        # generate an update
        update_fields = [field for field in list(mongo_data.keys()) if field not in self._primary_keys]
        update = {'$set': {}}
        for field in update_fields:
            update['$set'][field] = mongo_data[field]
        self._logger.debug(self._mongo_object_db_col.find(query).explain())  # check if the index is used
        self._logger.debug('found a document to update'
                           if self._mongo_object_db_col.count_documents(query) > 0
                           else 'inserting the document')

        await self._mongo_object_db_col.update_one(filter=query, update=update, upsert=True)

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
