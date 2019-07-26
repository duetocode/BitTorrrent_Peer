from .base import Handler
from bittorrent.protocol.message import Choke

class ChokeHandler(Handler):

    def messageReceived(self, message:Choke, protocol):
        protocol.choke = True