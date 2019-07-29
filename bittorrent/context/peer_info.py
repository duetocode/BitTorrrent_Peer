from typing import List

from .piece_info import PieceInfo
from .endpoint import Endpoint
class PeerInfo:

    def __init__(self, 
                 id:bytes=None, 
                 endpoint:Endpoint=None, 
                 pieces:List[PieceInfo]=None):
        self.id = id
        self.endpoint = endpoint
        self.pieces = pieces
        self.lastSeen = 0
        