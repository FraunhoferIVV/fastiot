import asyncio
from datetime import timedelta

from fastiot.core.app import FastIoTApp, BROKER_CONNECTION_KEY
from fastiot.core.broker_connection import BrokerConnection, BrokerConnectionImpl
from fastiot_sample_services.producer.sample_data_source import SampleDataSource


class MyApp(FastIoTApp):

    @subscribe @reply @stream
    async def asdf


    @loop
    async def produce(self):
        value = data_source.get_value()
        await broker_connection.send(
            subject=,
            msg=value
        )
        return asyncio.sleep(2)


if __name__ == '__main__':
    app = MyApp()
    app.run()
