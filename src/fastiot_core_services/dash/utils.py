""" This class holds some tools to work with Flask within SAM modules covering async and threading.

As of know it seems to be working but it is only lightly tested. Please use with caution!
"""
import json
import threading
from typing import Dict, List, Union

from werkzeug.serving import make_server

from fastiot.msg import Thing
from fastiot.msg.custom_db_data_type_conversion import to_mongo_data
from fastiot.util.object_helper import parse_object_list
from fastiot_core_services.dash.env import env_dash
from fastiot_core_services.dash.model.historic_sensor import ThingSeries


class ServerThread(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server('0.0.0.0', env_dash.dash_port, app, threaded=True)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


def thing_series_from_mongodb_data_set(data_set_list: List[Dict]) -> ThingSeries:
    if data_set_list:
        thing_list = parse_object_list(dict_list=data_set_list, data_model=Thing)
        dt_start = thing_list[0].timestamp
        dt_end = thing_list[-1].timestamp
        return ThingSeries(dt_start=dt_start, dt_end=dt_end, thing_list=thing_list)
    return ThingSeries()


def thing_series_to_mongodb_data_set(thing_series: ThingSeries) -> List[Dict]:
    return [to_mongo_data(timestamp=thing.timestamp, subject_name=thing.get_subject(thing.name).name,
                          msg=thing.dict()) for thing in thing_series.thing_list]


def thing_series_from_influxdb_data_set(json_str: Union[List, str]) -> ThingSeries:
    if json_str != '[]':
        results = json.loads(json_str)
        thing_list = [
            Thing(machine=record["machine"], name=record["_measurement"],
                  value=record["_value"], timestamp=record["_time"]) for record in results]
        dt_start = thing_list[0].timestamp
        dt_end = thing_list[-1].timestamp
        return ThingSeries(dt_start=dt_start, dt_end=dt_end, thing_list=thing_list)
    return ThingSeries()
