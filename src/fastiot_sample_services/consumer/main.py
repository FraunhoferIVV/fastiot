import logging

from fastiot.core.app import FastIoTApp
from fastiot.core.app_annotations import subscribe
from fastiot.msg.thing import Thing


class MyApp(FastIoTApp):

    @subscribe(subject=Thing.get_subject('my_sensor'))
    async def consume(self, msg):
        logging.info(msg)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    MyApp.main()
