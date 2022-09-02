import logging

import pymongo

from fastiot.core import FastIoTService, stream, Subject, subscribe
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.env import env_mongodb
from fastiot.env import env_mongodb_cols
from fastiot.msg.thing import Thing


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
    async def _cb_receive_data(self, topic: str,  msg: Thing):
        logging.info("Received message from sensor %s: %s" % (msg.name, str(msg)))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    TimeSeriesService.main()
