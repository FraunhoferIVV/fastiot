import logging

from fastiot.core.app import FastIoTService
from fastiot.core.app_annotations import subscribe
from fastiot.msg.thing import Thing


class MyService(FastIoTService):

    @subscribe(subject=Thing.get_subject('*'))
    async def consume(self, topic: str, msg: Thing):
        logging.info("%s: %s", topic, str(msg))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    MyService.main()
