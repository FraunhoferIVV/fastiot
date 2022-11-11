import logging


from fastiot.env.env import env_redis
from fastiot.msg.thing import Redis
from fastiot.core.serialization import serialize_to_bin, serialize_from_bin
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
        self.idCounter = 0


    async def _createId(self) -> int:
        if self.idCounter >= (self.maxDataSets *2):
            self.idCounter = 0
        while self.idCounter in self.usedIds:
            self.idCounter = self.idCounter + 1
        self.usedIds.append(self.idCounter)
        return self.idCounter

    async def sendData(self,data , source: str):
        id = await self._createId()
        client = await getRedisClient()
        data = serialize_to_bin(data.__class__, data)
        subject = Redis.get_subject(source)
        client.set(name=id, value=data)
        await self.broker_connection.publish(
            subject=subject,
            msg=Redis(id=id))
        logging.info("Saved data at %d from sensor %s",id , subject.name)
        await self.delete()

    async def getData(self, address: str):
        client = await getRedisClient()
        return serialize_from_bin("".__class__, client.get(address))



    async def delete(self):
        client = await getRedisClient()
        while len(self.usedIds) > self.maxDataSets:
            delete = self.usedIds[0]
            client.delete(delete)
            self.usedIds.remove(delete)
            logging.info("Removed Data with Id %d", delete)
