from .base import Handler
from bittorrent.protocol.message import Unchoke

class NotInterestedHandler(Handler):

    def messageReceived(self, message:Unchoke, protocol):
        protocol.interested = False