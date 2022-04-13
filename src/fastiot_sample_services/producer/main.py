import asyncio
from datetime import timedelta

from fastiot.core.app import FastIoTApp, BROKER_CONNECTION_KEY
from fastiot.core.broker_connection import BrokerConnection, BrokerConnectionImpl
from fastiot_sample_services.producer.sample_data_source import SampleDataSource

app = FastIoTApp()


class MyApp(FastIoTApp):

    @subscribe @reply @stream(subject=)
    async def asdf


    @loop(inject=[BROKER_CONNECTION_KEY, DATA_SOURCE_KEY])
    async def produce(self, broker_connection: BrokerConnection, data_source: SampleDataSource):
        value = data_source.get_value()
        await broker_connection.send(
            subject=,
            msg=value
        )
        return asyncio.sleep(2)


if __name__ == '__main__':
    app.run()
