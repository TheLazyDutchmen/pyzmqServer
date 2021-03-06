from typing import Callable
import zmq
import pickle
import threading
from abc import ABC, abstractmethod

from .events.event import Event
from .events.eventHandler import EventNotFound

context = zmq.Context()


class Connection:
    socket: zmq.Socket




class EventSender(Connection):
    
    def __init__(self, port: int) -> None:
        self.socket = context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{port}")

    def SendMessage(self, target: str, eventType: Event, data):
        target = target.encode('utf-8')
        data = pickle.dumps((eventType, data))

        self.socket.send_multipart((target, data))

class RequestSender(Connection):
    
    def __init__(self, serverIp: str, port: int) -> None:
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{serverIp}:{port}")

    def SendMessage(self, requestType: Event, data):
        event = pickle.dumps(requestType)
        data = pickle.dumps(data)

        self.socket.send_multipart((event, data))
        reply = pickle.loads(self.socket.recv())

        return reply



class Reciever(ABC):

    callback: Callable = print

    def SetCallback(self, callback: Callable) -> None:
        self.callback = callback

    def start(self, daemon: bool = True):
        loopThread = threading.Thread(target = self.startLoop)
        loopThread.setDaemon(daemon)
        loopThread.start()

    @abstractmethod
    def startLoop(self):
        pass

class EventReceiver(Connection, Reciever):
    
    def __init__(self, serverIp: str, port: int, daemon: bool = True) -> None:
        self.socket = context.socket(zmq.SUB)
        self.socket.connect(f"tcp://{serverIp}:{port}")

        self.start(daemon)

    def Subscribe(self, topic: str):
        self.socket.subscribe(topic)

    def startLoop(self):
        while True:

            target, data = self.socket.recv_multipart()
            target = target.decode('utf-8')
            data = pickle.loads(data)

            self.callback(target, data)

class RequestReceiver(Connection, Reciever):
    
    def __init__(self, port: int, daemon: bool = True) -> None:
        self.socket = context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{port}")

        self.start(daemon)

    def startLoop(self):
        while True:
            answer = False
            try:
                requestType, data = self.socket.recv_multipart()
                requestType: Event = pickle.loads(requestType)
                data = pickle.loads(data)

                answer = self.callback(requestType, data)
            except EventNotFound as e:
                answer = (False, e.message)
            finally:
                answer = pickle.dumps(answer)
                self.socket.send(answer)

