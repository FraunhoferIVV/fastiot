import datetime
import logging

from fastiot.core import FastIoTService, subscribe, reply
from fastiot.db.influxdb_helper_fn import get_async_influxdb_client_from_env
from fastiot.env.env import env_influxdb

from fastiot.msg.hist import HistObjectReq, HistObjectResp
from fastiot.msg.thing import Thing
from fastiot_core_services.time_series.env import time_series_env as env


class TimeSeriesService(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.write_api = None
        self.query_api = None
        self.counter = 0
        self.client = None

    async def _start(self):
        self.client = await get_async_influxdb_client_from_env()
        self.write_api = self.client.write_api()
        self.query_api = self.client.query_api()

    @subscribe(subject=Thing.get_subject(env.subscribe_subject))
    async def consume(self, msg: Thing):

        data = [{"measurement":
                     str(msg.name),
                 "tags":
                     {"machine": str(msg.machine)},
                 "fields":
                     {"value": str(msg.value) + " " + str(msg.unit)},
                 "time": msg.timestamp
                 }]
        await self.write_api.write(bucket=env_influxdb.bucket, org=env_influxdb.organisation, record=data, precision='ms')
        self.counter = self.counter + 1
        if self.counter >= 10:
            self.counter = 0
            logging.debug("10 datasets written")



    @reply(HistObjectReq.get_reply_subject(name=env.reply_subject))
    async def reply(self, request: HistObjectReq):
        query = await self.generate_query(request)

        results: list = []
        i: int = 0

        tables = await self.query_api.query(query, org=env_influxdb.organisation)

        for table in tables:
            for row in table:
                results.append({"machine": row.values.get("machine"),
                                "sensor": row.get_measurement(),
                                "value": row.get_value(),
                                "timestamp": row.get_time(),
                                })
        if len(results) > 0:
            return HistObjectResp(values=results)
        else:
            return HistObjectResp(values=results, error_msg="no data found", error_code="1")

    @staticmethod
    async def generate_query(request: HistObjectReq) -> str:
        limit: int = 20
        query: str = f'from(bucket: "{env_influxdb.bucket}")'
        if request.dt_start is not None:
            query = query + f'|> range(start: {request.dt_start.isoformat().split("+")[0]}Z'
            if request.dt_end is not None:
                query = query + f', stop: {request.dt_end.isoformat().split("+")[0]}Z'
            query = query + ')'
        else:
            start = datetime.datetime.utcnow() - datetime.timedelta(days=30)
            query = query + "|> range(start:" + str(start.isoformat().split("+")[0]) + "Z)"
        if request.sensor is not None:
            query = query + f'|> filter(fn: (r) => r["_measurement"] == "{request.sensor}")'
        if request.machine is not None:
            query = query + f'|>filter(fn: (r) => r["machine"] =="{request.machine}")'
        if request.limit is not None:
            limit = request.limit
        query = query + f'|> limit(n: {limit})' \
                        '|> group(columns:["time"])' \
                        '|> sort(columns: ["_time"])'
        if not request.query_dict is None and request.query_dict.type() == "str":
            query = request.query_dict
        return query

    async def _stop(self):
        await self.client.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    TimeSeriesService.main()
