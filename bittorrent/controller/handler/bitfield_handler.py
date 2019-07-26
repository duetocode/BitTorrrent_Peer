
from bittorrent.protocol.message import Bitfield

class BitfieldHandler:

    def __init__(self, torrentContext):
        self.torrentContext = torrentContext

    def messageReceived(self, message, protocol):
        # Update peer pieces list
        pass