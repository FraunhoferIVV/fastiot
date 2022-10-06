import asyncio
import datetime
import logging

from fastiot.core import FastIoTService, subscribe, reply
from fastiot.db.influxdb_helper_fn import get_client
from fastiot.env.env import env_influxdb

from fastiot.msg.hist import HistObjectReq, HistObjectResp
from fastiot.msg.thing import Thing


class TimeSeriesService(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.write_api = None
        self.query_api = None
        self.counter = 0
        self.client = None

    async def _start(self):
        self.client = await get_client()
        self.write_api = self.client.write_api()
        self.query_api = self.client.query_api()

    @subscribe(subject=Thing.get_subject('>'))
    async def consume(self, msg: Thing):
        self.client = await get_client()
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
            logging.debug("10 datapoints written")


    @reply(HistObjectReq.get_reply_subject(name="things"))
    async def reply(self, request: HistObjectReq):
        self.client = await get_client()
        limit: int = 20
        results: list = []
        query: str = f'from(bucket: "{env_influxdb.bucket}")'

        if not request.dt_start is None:
            query = query + f'|> range(start: {request.dt_start.isoformat().split("+")[0]}Z'
            if not request.dt_end is None:
                query = query + f', stop: {request.dt_end.isoformat().split("+")[0]}Z'
            query = query + ')'
        else:
            start = datetime.datetime.utcnow() - datetime.timedelta(days=30)
            query = query + "|> range(start:" + str(start.isoformat().split("+")[0]) + "Z)"

        if not request.sensor is None:
            query = query + f'|> filter(fn: (r) => r["_measurement"] == "{request.sensor}")'
        if not request.machine is None:
            query = query + f'|>filter(fn: (r) => r["machine"] =="{request.machine}")'
        if not request.limit is None:
            limit = request.limit
        query = query + f'|> limit(n: {limit})' \
                        '|> group(columns:["time"])' \
                        '|> sort(columns: ["_time"])'
        if not request.query_dict is None and request.query_dict.type() == "str":
            query = request.query_dict

        await asyncio.sleep(1)
        try:
            tables = await self.query_api.query(query, org=env_influxdb.organisation)
        except:
            logging.error("cannot query an empty Range, Please give valid Timeframe")
            return HistObjectResp(values=results, error_code=1, error_msg="cannot query an empty Range, Please give valid Timeframe")


        for table in tables:
            for row in table:
                results.append({"machine": row.values.get("machine"),
                                "sensor": row.get_measurement(),
                                "value": row.get_value(),
                                "timestamp": row.get_time(),
                                })
        return HistObjectResp(values=results)

    async def _stop(self):
        await self.client.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    TimeSeriesService.main()
