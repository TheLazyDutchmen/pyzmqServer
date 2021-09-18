from typing import Callable

from . import Connection
from .events.event import Event



class Client:

    def __init__(self, serverIp: str, eventPort: int, requestSendPort: int, requestReceivePort: int):
        self.eventConnection = Connection.EventReceiver(serverIp, eventPort)
        self.requestSendConnection = Connection.RequestSender(serverIp, requestSendPort)
        # self.requestReceiveConnection = Connection.RequestReceiver(requestReceivePort)

    def SetEventCallback(self, eventCallback: Callable) -> None:
        self.eventConnection.SetCallback(eventCallback)

    def SetRequestCallback(self, requestCallback: Callable) -> None:
        self.requestReceiveConnection.SetCallback(requestCallback)

    def SendRequest(self, requestType: str, data):
        event = Event(requestType)
        reply = self.requestSendConnection.SendMessage(event, data)

        return reply

    def Subscribe(self, topic: str):
        self.eventConnection.Subscribe(topic)
