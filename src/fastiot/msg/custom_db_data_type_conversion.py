from datetime import datetime
from typing import Dict


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
    _ = {mongo_data.pop(key) for key in mongo_base_dict}
    return mongo_data
