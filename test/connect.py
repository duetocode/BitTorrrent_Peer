import logging
import sys
import binascii
import shutil
import signal
from twisted.internet import reactor
from bittorrent import BitTorrentController
from bittorrent.context import PeerInfo, TorrentContext

shutil.rmtree('./downloads')

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().info('Starting test...')

torrentFile = 'test/resources/debian-9.9.0-amd64-netinst.iso.torrent'
torrentContext = TorrentContext.createFromFile(torrentContext)

peerInfo = PeerInfo

endpoint = TCP4ClientEndpoint(self.reactor, 
                                peerInfo.endpoint.host, 
                                peerInfo.endpoint.port)
                                
protocol = BitTorrentProtocol(
    torrentContext=self.torrentContext,
    protocolDelegation=self.connectionScheduler, 
    messageHandler=self.messageHandler,
    peerInfo=peerInfo,
    initiator=True)
connectProtocol(endpoint, protocol)
self.logger.debug('Initiate new connection to %s', peerInfo.endpoint)
return protocol


def signal_handler(signo, frame):
    print('Signal received: ', signo)
    if signo == signal.SIGTERM:
        reactor.stop()

signal.signal(signal.SIGTERM, signal_handler)
reactor.run()