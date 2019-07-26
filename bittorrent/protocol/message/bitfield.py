from bitstring import BitArray
from .main import Message
from bittorrent.piece_info import PieceInfo, PieceState

class Bitfield(Message):

    def __init__(self, pieces:List[PieceInfo]):
        self.id = 5
        self.pieces = pieces
        
    @classmethod
    def parse(clazz, rawData:bytes) -> Bitfield:
        # parse rawdata into piece info list
        bitArray = BitArray(rawData)
        
        pieces = list([PieceInfo(i, PieceState.Have if v else PieceState.NotHave) for i, v in enumerate(bitArray)])

        return Bitfield(pieces)

    def serialize(self) -> bytes:
        # serialize piece info list into bytestring
        bitArray = BitArray([p.state == PieceState.Have for p in self.pieces])
        return bitArray.tobytes()