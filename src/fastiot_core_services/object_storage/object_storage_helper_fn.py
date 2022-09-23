from typing import Dict


def build_mongo_data(timestamp: str, subject_name: str, msg: Dict) -> Dict:
    mongo_data_base = {'_timestamp': timestamp, '_subject': subject_name}
    mongo_data = mongo_data_base | msg
    return mongo_data


