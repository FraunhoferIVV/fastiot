import re
from typing import Dict

from fastiot.msg.hist import HistObjectReq


def build_query_dict(hist_object_req: HistObjectReq) -> Dict:
    """
    This function parses the HistObjectReq instance, and build the query dict to search data in database
    """
    query_dict = {}
    if hist_object_req.subject_name is not None:
        subject_substr = re.sub("\ |\*|", '', hist_object_req.subject_name).split('..')[0]
        query_dict = query_dict | {"_subject": {'$regex': subject_substr}}
    if hist_object_req.dt_start is not None and hist_object_req.dt_end is None:
        query_dict = query_dict | {"_timestamp": {'$gte': hist_object_req.dt_start}}
    if hist_object_req.dt_end is not None and hist_object_req.dt_start is None:
        query_dict = query_dict | {"_timestamp": {'$lte': hist_object_req.dt_end}}
    if hist_object_req.dt_start is not None and hist_object_req.dt_end is not None:
        query_dict = query_dict | {"_timestamp": {'$gte': hist_object_req.dt_start, '$lte': hist_object_req.dt_end}}
    if hist_object_req.raw_query is not None:
        query_dict = query_dict | hist_object_req.raw_query

    return query_dict

