from .base import Handler
from bittorrent.protocol.message import Unchoke

class InterestedHandler(Handler):

    def messageReceived(self, message:Unchoke, protocol):
        protocol.interested = True