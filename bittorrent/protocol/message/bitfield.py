from typing import List
from bitstring import BitArray
from .main import Message
from bittorrent.context import PieceInfo, PieceState

class Bitfield(Message):

    def __init__(self, pieces:List[PieceInfo]=None):
        self.id = 5
        if pieces is not None:
            self.array = BitArray([p.state == PieceState.Have for p in pieces])
        else:
            self.array = None
        
    @classmethod
    def parse(clazz, rawData:bytes) -> 'Bitfield':
        # parse rawdata into piece info list
        bitfield = Bitfield()
        bitfield.array = BitArray(rawData)

        return bitfield

    def serialize(self) -> bytes:
        # serialize piece info list into bytestring
        return self.array.tobytes()