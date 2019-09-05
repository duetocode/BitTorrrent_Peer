
from bittorrent.protocol.message import Bitfield

class BitfieldHandler:

    def __init__(self, torrentContext):
        self.torrentContext = torrentContext

    def messageReceived(self, message:Bitfield, protocol):
        # Update peer pieces list
        protocol.peerInfo.pieces = message.array