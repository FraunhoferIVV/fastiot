import asyncio
import logging

from fastiot.core import FastIoTService
from fastiot.core.serialization import serialize_to_bin
from fastiot.env.env import env_redis
from fastiot.msg.thing import Redis
import redis

class RedisClient:
    client = None

async def connectRedis():
    client = redis.Redis(
        host=env_redis.host,
        port=env_redis.port)
    return client

async def getRedisClient():
    if RedisClient.client is None:
        RedisClient.client = await connectRedis()
    return RedisClient.client


class RedisHelper:

    def __init__(self, broker_connection):
        self.broker_connection = broker_connection
        self.usedIds = []
        self.maxDataSets = 10


    async def _createId(self) -> int:
        i: int = 0
        while i in self.usedIds:
            i = i + 1
        self.usedIds.append(i)
        return i

    async def sendData(self,data, source: str):
        id = await self._createId()
        client = await getRedisClient()
        client.set(name=id, value=data)
        subject = Redis.get_subject(source)
        await self.broker_connection.publish(
            subject=subject,
            msg=Redis(id=id))
        logging.info("Saved data at %d from sensor %s",id, subject.name)
        await self.delete()

    async def getData(self, address: str):
        client = await getRedisClient()
        data = client.get(address)
        return data

    async def delete(self):
        client = await getRedisClient()
        while len(self.usedIds) > self.maxDataSets:
            delete = self.usedIds[0]
            client.delete(delete)
            self.usedIds.remove(delete)
            logging.debug("removed Data with Id %d", delete)
