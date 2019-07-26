from .base import Handler
from bittorrent.protocol.message import Unchoke

class UnchokeHandler(Handler):

    def messageReceived(self, message:Unchoke, protocol):
        protocol.choke = False