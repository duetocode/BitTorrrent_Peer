import struct
from .main import Message

class Port(Message):

    def __init__(self, port=None):
        self.id = 9
        self.port = port
        
    @classmethod
    def parse(clazz, rawData):
        return Port(port=struct.unpack('!H', rawData)[0])

    def serialize(self) -> bytes:
        return struct.pack('!H', self.port)