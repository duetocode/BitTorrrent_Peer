from typing import List

from .piece_info import PieceInfo
from .endpoint import Endpoint
class PeerInfo:

    def __init__(self, 
                 peerId:bytes=None, 
                 endpoint:Endpoint=None, 
                 pieces:List[PieceInfo]=None):
        self.peerId = peerId
        self.endpoint = endpoint
        self.pieces = pieces
        