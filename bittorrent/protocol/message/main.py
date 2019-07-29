import struct

class Message:

    def serialize(self):
        raise NotImplementedError()

    def toBytes(self):
        """Serialize message object into BitTorrent protocol message"""
        payload = self.serialize()
        length = struct.pack('!I', len(payload) + 1)

        return [length, bytes([self.id]), payload]
        


class EmptyMessage(Message):

    def serialize(self):
        return b''