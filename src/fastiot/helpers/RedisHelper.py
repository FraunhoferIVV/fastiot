from fastiot.core import FastIoTService
from fastiot.msg.thing import Address


class RedisHelper(FastIoTService):

    async def sendData(self,data, subject: str):


        #client = getClient() # gibt client für die Daten
        #adress = saveData() # hochzählende addrese für die daten
        await self.broker_connection.publish(
            subject=subject,
            msg=Address(address=adress, client=client, publisher=subject)
            )
        )

    async def getData(address:str, client):
            data = client.getAddress(address)
            deleteClient(client) # client wird nach bestimmter zeit gelöscht
            return data

    async def delete():
        # löscht Daten nach bestimmter zeit
        pass