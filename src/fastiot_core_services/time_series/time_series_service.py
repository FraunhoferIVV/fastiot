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
        self.msg_counter_ = 0
        self.client = None

    async def _start(self):
        self.client = await get_async_influxdb_client_from_env()

    async def _stop(self):
        await self.client.close()

    @subscribe(subject=Thing.get_subject(env.subscribe_subject))
    async def consume(self, msg: Thing):

        data = [{"measurement": str(msg.name),
                 "tags": {"machine": str(msg.machine),
                          "unit": str(msg.unit)},
                 "fields": {"value": msg.value},
                 "time": msg.timestamp
                 }]
        await self.client.write_api().write(bucket=env_influxdb.bucket, org=env_influxdb.organisation,
                                            record=data, precision='ms')
        query = \
            f'from(bucket: "{env_influxdb.bucket}") ' \
            '|> range(start: 2019-07-25T21:47:00Z)'
        tables = await self.client.query_api().query(query, org=env_influxdb.organisation)
        self.msg_counter_ = self.msg_counter_ + 1
        if self.msg_counter_ >= 10:
            self.msg_counter_ = 0
            logging.debug("10 datasets written")

    @reply(HistObjectReq.get_reply_subject(name=env.request_subject))
    async def reply(self, request: HistObjectReq):
        query = await self.generate_query(request)

        results: list = []
        tables = await self.client.query_api().query(query, org=env_influxdb.organisation)

        for table in tables:
            for row in table:
                results.append({"machine": row.values.get("machine"),
                                "sensor": row.get_measurement(),
                                "value": row.get_value(),
                                "unit": row.values.get("unit"),
                                "timestamp": row.get_time(),
                                })
        if len(results) > 0:
            return HistObjectResp(values=results)

        logging.debug("No data found. Returning error code 1.")
        return HistObjectResp(values=results, error_msg="no data found", error_code=1)

    @staticmethod
    async def generate_query(request: HistObjectReq) -> str:

        if request.raw_query and isinstance(request.raw_query, str):
            return request.raw_query

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

        query = query + f'|> limit(n: {request.limit})' \
                        '|> group(columns:["time"])' \
                        '|> sort(columns: ["_time"])'

        return query


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    TimeSeriesService.main()
