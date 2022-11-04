import logging

from fastiot.core import FastIoTService
from fastiot.env.env import env_redis
from fastiot.msg.thing import Redis
import redis

class RedisClient:
    def __int__(self):
        self.client = None

    async def connect(self):
        self.client = redis.Redis(
            host=env_redis.host,
            port=env_redis.port)
        return self.client.ping

    async def getclient(self):
        if self.client is None:
            self.connect()
        return self.client

"""
class RedisHelper(FastIoTService):


    async def sendData(self,data, subject: str):


        #client = getClient() # gibt client für die Daten
        #saveData() # hochzählende addrese für die daten
        await self.broker_connection.publish(
            subject=subject,
            msg=Redis(address=adress, client=client, publisher=subject)
            )
        )

    async def getData(address:str, client):
            data = client.getAddress(address)
            return data

    async def delete():
        # löscht Daten nach bestimmter zeit
        pass
"""