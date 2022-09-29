from datetime import datetime
from typing import Dict

from fastiot.util.dict_helper import dict_subtract
from fastiot.msg.hist import HistObjectReq


def to_mongo_data(timestamp: datetime, subject_name: str, msg: Dict) -> Dict:
    """
    This function helps to convert msg to a mongodb data set.
    """
    mongo_data_base = {'_timestamp': timestamp, '_subject': subject_name}
    mongo_data = mongo_data_base | msg
    return mongo_data


def from_mongo_data(mongo_data: dict) -> Dict:
    """
    This function helps to convert mongodb data set back to the msg.
    """
    mongo_base_dict = {'_id': 'mongo_id', '_subject': 'subject_name', '_timestamp': 'timestamp'}
    object_data = dict_subtract(mongo_data, mongo_base_dict)
    return object_data


def build_query_dict(hist_object_req: HistObjectReq) -> Dict:
    """
    This function parses the HistObjectReq instance, and build the query dict to search data in database
    """
    query_dict = {}
    if hist_object_req.subject_name is not None:
        query_dict = query_dict | {"_subject": hist_object_req.subject_name}
    if hist_object_req.dt_start is not None and hist_object_req.dt_end is None:
        query_dict = query_dict | {"_timestamp": {'$gte': hist_object_req.dt_start}}
    if hist_object_req.dt_end is not None and hist_object_req.dt_start is None:
        query_dict = query_dict | {"_timestamp": {'$lte': hist_object_req.dt_end}}
    if hist_object_req.dt_start is not None and hist_object_req.dt_end is not None:
        query_dict = query_dict | {"_timestamp": {'$gte': hist_object_req.dt_start, '$lte': hist_object_req.dt_end}}
    if hist_object_req.query_dict is not None:
        query_dict = query_dict | hist_object_req.query_dict

    return query_dict
