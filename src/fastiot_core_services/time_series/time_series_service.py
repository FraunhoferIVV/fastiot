import logging

import pymongo
from pymongo.collection import Collection

from fastiot.core import FastIoTService, stream, Subject, subscribe
from fastiot.core.core_uuid import get_uuid
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env, time_series_data_to_mongodb_data_set
from fastiot.env import env_mongodb
from fastiot.env import env_mongodb_cols
from fastiot.msg.thing import Thing
from fastiot.msg.time_series_msg import TimeSeriesData


class TimeSeriesService(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._db_client = get_mongodb_client_from_env()
        database = self._db_client.get_database(env_mongodb.name)
        self._time_series_db_col = database.get_collection(env_mongodb_cols.time_series)

        for column_name in ["name", "dt_start", "dt_end", "modified_at"]:
            self._db_client.create_index(collection=self._time_series_db_col,
                                         index=[(column_name, pymongo.ASCENDING)],
                                         index_name=f"{column_name}_ascending")

    async def _start(self):
        pass

    async def _stop(self):
        pass

    @subscribe(subject=Thing.get_subject('*'))
    async def _cb_receive_data(self, topic: str, msg: Thing):
        logging.info("Received message from sensor %s: %s" % (msg.name, str(msg)))
        time_seires_data = self._convert_thing_message_to_time_series_data(msg)
        self._insert_or_update_time_series(self._time_series_db_col, time_seires_data)

    def _convert_thing_message_to_time_series_data(self, msg: Thing) -> TimeSeriesData:
        time_series_data = TimeSeriesData(id=get_uuid(),
                                          name=msg.name,
                                          service_id=msg.machine,
                                          measurement_id=msg.measurement_id,
                                          dt_start=msg.timestamp,
                                          dt_end=msg.timestamp,
                                          modified_at=msg.timestamp,
                                          values=msg.value)
        return time_series_data

    @staticmethod
    def _insert_or_update_time_series(db_col: Collection, time_series: TimeSeriesData):
        filter = {
            'name': time_series.name,
            'service_id': time_series.service_id,
            'measurement_id': time_series.measurement_id,
            'dt_start': time_series.dt_start
        }
        update_result = db_col.update_one(
            filter=filter,
            update={
                "$set": {
                    'dt_end': time_series.dt_end,
                    'modified_at': time_series.modified_at,
                    'values': time_series.values
                }
            }
        )
        if update_result.matched_count == 0:
            d = time_series_data_to_mongodb_data_set(time_series)
            db_col.insert_one(d)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    TimeSeriesService.main()
