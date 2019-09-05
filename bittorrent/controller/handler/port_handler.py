import logging
from bittorrent.protocol.message import Port

class PortHandler:

    def __init__(self, torrentContext):
        self.torrentContext = torrentContext
        self.logger = logging.getLogger('protocol.handlers.port')
        

    def messageReceived(self, message:port, protocol):
        logger.debug('New DHT peer found: %s:%d', protocol.peerInfo.endpoint.host, message.sport)
        