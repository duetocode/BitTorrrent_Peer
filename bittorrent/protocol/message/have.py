from .main import Message
from bittorrent.context import PieceInfo

class Have(Message):

    def __init__(self, pieceInfo:PieceInfo):
        self.id = 5
        self.pieceInfo = pieceInfo
        
    @classmethod
    def parse(clazz, rawData):
        # parse rawdata into piece info 
        pass

    def serialize(self):
        # serialize piece info into bytestring
        pass