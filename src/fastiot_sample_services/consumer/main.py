import logging

from fastiot.core.app import FastIoTApp

app = FastIoTApp()


class MyApp(FastIoTApp):

    @subscribe(subject=asdf)
    async def consume(self, msg):
        logging.info(msg)


if __name__ == '__main__':
    app.run()
