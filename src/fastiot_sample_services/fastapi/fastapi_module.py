import asyncio
import logging
import os

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from fastiot.core import FastIoTService, subscribe
from fastiot.msg.thing import Thing
from fastiot_sample_services.fastapi.env import env_fastapi
from fastiot_sample_services.fastapi.model import Request, Response
from fastiot_sample_services.fastapi.uvicorn_server import UvicornAsyncServer


class FastAPIModule(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app = FastAPI()
        self._register_routes()
        self.server = UvicornAsyncServer(self.app, port=env_fastapi.fastapi_port)

        self.message_received = asyncio.Event()
        self.last_msg = None
        # We have an event trigger whenever a message arrives via nats
        # This will than trigger the websocket to send some data

    def _register_routes(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.app.websocket("/ws")(self.serve_websocket)
        self.app.get("/get_some_data")(self._handle_get)
        self.app.post("/post_some_data")(self._handle_post)
        self.app.mount("/",
                       StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"),
                                   html=True),
                       name="static")
        # This will serve static files created with a vue.js framework.

    async def _start(self):
        """ Methods to start once the module is initialized """
        await self.server.up()

    async def _stop(self):
        """ Methods to call on module shutdown """
        await self.server.down()

    @subscribe(subject=Thing.get_subject('*'))
    async def _on_data_received(self, _, msg: Thing):
        """ Callback whenever some new machine data arrives """
        self.last_msg = msg
        self.message_received.set()

    def _handle_get(self):
        """ Simple method to reply to a get request """
        return {"hello_world": "Good morning!",
                "last_message": self.last_msg}

    def _handle_post(self, message: Request):
        """
        Simple handling of Post Request

        the = Body(...) is needed as we don’t use pydantic classes,
        s. https://fastapi.tiangolo.com/tutorial/body-multiple-params/#embed-a-single-body-parameter for more details
        """

        mean = sum(message.req_value) / len(message.req_value)
        return Response(resp_value=mean)

    async def serve_websocket(self, websocket: WebSocket):
        """ Demonstration of using websockets

        You need to send one char first before all new arriving machine data will be sent to the client

        https://fastapi.tiangolo.com/advanced/websockets/
        """
        await websocket.accept()

        await websocket.send_text("Hello world!")
        await websocket.send_text("Send any char to start!")

        received = await websocket.receive_text()
        logging.info("Received data: %s", received)

        while True:
            await self.message_received.wait()
            await websocket.send_text(f"Received message from sensor {self.last_msg.name}: {str(self.last_msg.value)}")
            self.message_received.clear()
