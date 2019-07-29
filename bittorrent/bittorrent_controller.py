import logging
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

from .context import PeerInfo, TorrentContext
from .discovery import PeerDiscovery
from .storage import Storage
from .controller import ConnectionScheduler
from .protocol import BitTorrentProtocol


class BitTorrentController:

    """Main controller of the BitTorrent system."""

    def __init__(self, torrentContext, reactor):
        self.torrentContext = torrentContext
        self.reactor = reactor
        self.connectionScheduler = ConnectionScheduler(self)
        self.peerDiscovery = PeerDiscovery(torrentContext, self.connectionScheduler)
        self.storage = Storage(torrentContext, self)
        self.logger = logging.getLogger(f'BitTorrentController')

    @classmethod
    def createFromTorrentFile(clz, file, root, reactor) -> 'BitTorrentController':
        torrentContext = TorrentContext.createFromFile(file)
        torrentContext.root = root
        return BitTorrentController(torrentContext, reactor)

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
        #endpoint = TCP4ClientEndpoint(self.reactor, 
        #                              peerInfo.endpoint.host, 
        #                              peerInfo.endpoint.port)
                                      
        #protocol = BitTorrentProtocol(self.connectionScheduler, self.messageHandler, initiator=True)
        #connectProtocol(endpoint, protocol)
        self.logger.debug('Initiate new connection to %s', peerInfo.endpoint)
        #return protocol
        return peerInfo

    # -- Storage Delegation --
    def peiceDownloaded(self, pieceIndex):
        logger.debug('Piece with index of %d has been downloaded.', pieceIndex)