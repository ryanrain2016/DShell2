from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import asyncssh
import json, sys
import asyncio


class MySSHClientSession(asyncssh.SSHClientSession):
    def __init__(self, consumer):
        self.consumer = consumer

    def data_received(self, data, datatype):
        # async_to_sync(self.consumer.send)(data)
        asyncio.ensure_future(self.consumer.send(data))

    def connection_lost(self, exc):
        if exc:
            print('SSH session error: ' + str(exc), file=sys.stderr)

class MyWsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # print(dir(self))
        # print(self.channel_name)
        await self.accept()
        self.host = None
        self.port = None
        self.username = None
        self.passwd = None
        self.sshchannel = None
        self.sshconnection = None

    async def disconnect(self, close_code):
        self.sshchannel.close()
        self.sshconnection.close()
        self.sshchannel = None
        self.sshconnection = None

    async def receive(self, text_data=None, bytes_data=None):
        if self.sshchannel is None:
            hostinfo = json.loads(text_data)
            hostinfo['port'] = int(hostinfo['port'])
            self.host = hostinfo.get('host')
            self.port = hostinfo.get('port')
            self.username = hostinfo.get('username')
            self.passwd = hostinfo.get('passwd')
            await self.send('connecting')
            self.sshconnection = await asyncssh.connect(self.host, self.port, 
                                        username=self.username, 
                                        password=self.passwd, 
                                        known_hosts=None)
            self.sshchannel, _ = await self.sshconnection.create_session(lambda:MySSHClientSession(self), term_type='xterm')
            await self.send('\rconnected....\n')
        else:
            self.sshchannel.write(text_data)

    async def reply(self, message):
        text_data = message.get('text_data')
        bytes_data = message.get('bytes_data')
        await self.send(text_data=text_data, bytes_data=bytes_data)



