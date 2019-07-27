import logging
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

from .context import PeerInfo
from .discovery import PeerDiscovery
from .storage import Storage
from .controller import ConnectionScheduler, MessageHandler
from .protocol import BitTorrentProtocol


class BitTorrentController:

    """This is the facade of the controller system."""

    def init(self, torrentContext, reactor):
        self.torrentContext = torrentContext
        self.reactor = reactor
        self.connectionScheduler = ConnectionScheduler(self)
        self.peerDiscovery = PeerDiscovery(torrentContext, self.connectionScheduler)
        self.storage = Storage(torrentContext)
        self.messageHandler = MessageHandler(self)
        self.logger = logging.getLogger(f'BitTorrentController')
        self.connections = {}

    def start(self):
        self.storage.start()
        if not self.storage.isFinished():
            # Start downloading if it is not complished
            self.connectionScheduler.start()
            self.peerDiscovery.start()

    def shutdown(self):
        self.connectionScheduler.shutdown()
        self.peerDiscovery.shutdown()
        self.storage.shutdown()

    def downloadFinished(self):
        if storage.verify():
            self.connectionScheduler.shutdown()
            self.peerDiscovery.shutdown()

    # -- ConnectionSchedulerDelegation --
    def initiateNewConnection(self, peerInfo:PeerInfo):
        endpoint = TCP4ClientEndpoint(self.reactor, *peerInfo.endpoint[:2])
        protocol = BitTorrentProtocol(self.connectionScheduler, self.messageHandler, initiator=True)
        connectProtocol(endpoint, protocol)
        logger.debug('Initiate new connection to %s:%d', *peerInfo.endpoint[:2])
        return protocol