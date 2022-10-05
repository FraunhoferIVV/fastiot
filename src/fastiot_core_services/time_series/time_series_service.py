import datetime
import logging

import typer

from influxdb_client.client.write_api import ASYNCHRONOUS
from fastiot.core import FastIoTService, subscribe, reply
from fastiot.db.influxdb_helper_fn import get_influxdb_client_from_env
from fastiot.env.env import env_influxdb

from fastiot.msg.hist import HistObjectReq, HistObjectResp
from fastiot.msg.thing import Thing


class TimeSeriesService(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = get_influxdb_client_from_env()
        self.write_api = self.client.write_api(write_options=ASYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.counter = 0

    @subscribe(subject=Thing.get_subject('>'))
    async def consume(self, msg: Thing):
        data = [{"measurement":
                     str(msg.name),
                 "tags":
                     {"machine": str(msg.machine)},
                 "fields":
                     {"value": str(msg.value) + " " + str(msg.unit)},
                 "time": msg.timestamp
                 }]
        self.write_api.write(bucket=env_influxdb.bucket, org=env_influxdb.organisation, record=data, precision='ms')
        self.counter = self.counter + 1
        if self.counter >= 10:
            self.counter = 0
            logging.debug("10 datapoints written")

    @reply(HistObjectReq.get_reply_subject(name="things"))
    async def reply(self, request: HistObjectReq):
        limit: int = 20
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
                        '|> sort(columns: ["time"])'
        if not request.query_dict is None and request.query_dict.type() == "str":
            query = request.query_dict

        try:
            tables = self.query_api.query(query, org=env_influxdb.organisation)
        except:
            logging.error("cannot query an empty Range, Please give valid Timeframe")
            raise typer.Exit(1)

        results = []
        for table in tables:
            for row in table:
                results.append({"machine": row.values.get("machine"),
                                "sensor": row.get_measurement(),
                                "value": row.get_value(),
                                "timestamp": row.get_time(),
                                })
        return HistObjectResp(values=results)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    TimeSeriesService.main()
