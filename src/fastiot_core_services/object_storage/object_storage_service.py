import re
import time
from typing import List, Dict

import pymongo

from fastiot.core import FastIoTService, Subject
from fastiot.core.subject_helper import sanitize_pub_subject_name, filter_specific_sign
from fastiot.core.time import get_time_now
from fastiot.env import env_basic, env_mongodb
from fastiot.msg.custom_db_data_type_conversion import to_mongo_data, from_mongo_data
from fastiot.msg.hist import HistObjectReq, HistObjectResp
from fastiot_core_services.object_storage.config_model import ObjectStorageConfig, SubscriptionConfig
from fastiot_core_services.object_storage.mongodb_handler import MongoDBHandler
from fastiot_core_services.object_storage.object_storage_helper_fn import build_query_dict


class ObjectStorageService(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mongodb_handler = MongoDBHandler()
        self.database = self._mongodb_handler.get_database(env_mongodb.name)
        self.service_config = ObjectStorageConfig.from_service(self)
        if not self.service_config.subscriptions:
            self._logger.error('No subscriptions configured in configuration file for object storage. Aborting.')
            time.sleep(10)
            raise RuntimeError

        self._create_index()


    def _create_index(self):

        for collection, index_config in self.service_config.search_index.items():
            for index in index_config:
                if "," in index:  # Build compound index
                    self._logger.warning("Using a list seperated by ',' is deprecated. Please convert your configuration "
                                         "to a proper YAML list.")
                    indices = index.split(",")
                    index = [i.strip() for i in indices]

                if isinstance(index, list):
                    index = list(zip(index,
                                     map(lambda index_name:
                                         pymongo.ASCENDING if index_name != '_timestamp' else pymongo.DESCENDING,
                                         index)))
                    # the later the _timestamp in mongo_data - the more time relevant query results
                    self._logger.debug("Created compound index: '%s'", index)

                else:
                    index = [(index, pymongo.ASCENDING)]

                self._mongodb_handler.create_index(collection=self.database[collection],
                                                   index=index,
                                                   index_name="compound_index")

    async def _start(self):

        for subject_name, subscription_config in self.service_config.subscriptions.items():
            subject = Subject(name=sanitize_pub_subject_name(subject_name), msg_cls=dict)
            await self.broker_connection.subscribe(subject=subject, cb=self._cb_receive_data)

            if not subscription_config.reply_subject_name:
                self._logger.warning("Please set `reply_subject_name` in your configuration.\n"
                                     "Using `subject_name` for receiving and sending is deprecating.")
                subscription_config.reply_subject_name = subject_name

            subscription_config.reply_subject_name = filter_specific_sign(subscription_config.reply_subject_name)
            reply_subject = HistObjectReq.get_reply_subject(name=subscription_config.reply_subject_name)
            await self.broker_connection.subscribe_reply_cb(subject=reply_subject, cb=self._cb_reply_hist_object)

    async def _cb_receive_data(self, subject_name: str, msg: dict):

        subscription_config = self._find_matching_subject(subject_name)

        self._logger.debug("Received message %s", str(msg))
        # True for things; Possibly False for other messages
        if 'timestamp' in list(msg.keys()):
            timestamp = msg['timestamp']
        else:
            timestamp = get_time_now()
        mongo_data = to_mongo_data(timestamp=timestamp, subject_name=subject_name, msg=msg)
        self._logger.debug("Converted Mongo data is %s", mongo_data)

        if not subscription_config.enable_overwriting:
            self.database[subscription_config.collection].insert_one(mongo_data)
        else:
            # the last overwriting data should be saved (overwriting has to be asynchron)
            self._overwrite_data(mongo_data, subscription_config)

    def _find_matching_subject(self, subject_name: str) -> SubscriptionConfig:
        if len(self.service_config.subscriptions) == 0:  # Quick fix for most tasks
            return list(self.service_config.subscriptions.values())[0]

        for subscription_name in self.service_config.subscriptions.keys():
            regex =r'v1\.' + subscription_name.replace('.', r'\.').replace("*", r"[^\.]*").replace(">", r"\..*") + '$'
            if re.finditer(regex, subject_name):
                return self.service_config.subscriptions[subscription_name]


    def _overwrite_data(self, mongo_data, subscription_config: SubscriptionConfig):

        primary_keys = subscription_config.identify_object_with
        collection = self.database[subscription_config.collection]

        # generate upsert query
        query = {}
        for key_name in primary_keys:
            query[key_name] = mongo_data[key_name]
        # generate an update
        update_fields = [field for field in list(mongo_data.keys()) if field not in primary_keys]
        update = {'$set': {}}
        for field in update_fields:
            update['$set'][field] = mongo_data[field]
        if env_basic.log_level <= 10:
            self._logger.debug("Index used by MongoDB: %s", collection.find(query).explain())
            self._logger.debug('found a document to update' if collection.count_documents(query) > 0
                               else 'inserting the document')

        collection.update_one(filter=query, update=update, upsert=True)

    async def _cb_reply_hist_object(self, subject: str, hist_object_req: HistObjectReq) -> HistObjectResp:

        sub_config = [c for c in self.service_config.subscriptions.values() if
                      HistObjectReq.get_reply_subject(c.reply_subject_name).name == subject][0]

        self._logger.debug("Received request on subject %s with message %s", subject, hist_object_req)
        query_dict = build_query_dict(hist_object_req=hist_object_req)
        query_results = self._query_db(subscription_config= sub_config,
                                       query_dict=query_dict, limit_nr=hist_object_req.limit)
        values = [from_mongo_data(result) for result in query_results]
        if values:
            hist_object_resp = HistObjectResp(values=values)
        else:
            hist_object_resp = HistObjectResp(
                error_msg='No query results from Mongodb, please check Connection or query',
                values=values)
        return hist_object_resp

    def _query_db(self, subscription_config: SubscriptionConfig, query_dict: Dict, limit_nr: int) -> List:
        collection = self.database[subscription_config.collection]
        return list(collection.find(query_dict).limit(limit_nr))
