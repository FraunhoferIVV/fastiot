import logging

import redis

from fastiot.core.serialization import serialize_to_bin, serialize_from_bin
from fastiot.env.env import env_redis
from fastiot.msg import RedisMsg


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
    """
    Saves files in the redis Database and sends the ID of the files  as  :class:`fastiot.msg.redis.RedisMsg`.

    You can send files by using :meth:`send_data` you must specify the data to send and the subject under which the data
    should be published. The max number of Datasets you can store at once is specified by :var: `max_data_sets` .
    If you add a Dataset above the given limit the first Dataset stored is deleted. When you have problems that an ID
    is overwritten before you accessed the data you can change the :var:`id_buffer` to have more Ids before an ID is
    reused.

    You can access the stored data with :meth:`get_data`. The Id of the Data has to be provided. and the returned data
    will be deserialized with :meth:`fastiot.core.serialization.serialize_from_bin`.
    """

    def __init__(self, broker_connection):
        self.broker_connection = broker_connection
        self.used_ids = []
        self.max_data_sets = 100
        """ The max number of Datasets you can store at once """
        self.id_counter = 0
        self.id_buffer = 2
        """ :var:`max_data_sets` * :var:`id_buffer` is the total number of Ids, used before an id is overwritten """

    async def _create_id(self) -> int:
        if self.id_counter >= (self.max_data_sets * self.id_buffer):
            self.id_counter = 0
        while self.id_counter in self.used_ids:
            self.id_counter = self.id_counter + 1
        self.used_ids.append(self.id_counter)
        return self.id_counter

    async def send_data(self, data, subject):
        database_id = await self._create_id()
        client = await getRedisClient()
        data = serialize_to_bin(data.__class__, data)
        await self.delete()
        client.set(name=database_id, value=data)
        await self.broker_connection.publish(
            subject=subject,
            msg=RedisMsg(id=database_id))
        logging.info("Saved data at %d from  %s", database_id, subject.name)

    async def get_data(self, address: str):
        client = await getRedisClient()
        return serialize_from_bin("".__class__, client.get(address))

    async def delete(self):
        client = await getRedisClient()
        while len(self.used_ids) > self.max_data_sets:
            delete = self.used_ids[0]
            client.delete(delete)
            self.used_ids.remove(delete)
            logging.debug("Removed Data with Id %d", delete)

    async def deleteall(self):
        client = await getRedisClient()
        while len(self.used_ids) > 0:
            delete = self.used_ids[0]
            client.delete(delete)
            self.used_ids.remove(delete)
            logging.debug("Removed Data with Id %d", delete)
