import logging
import sys
import binascii
import shutil
import signal
from twisted.internet import reactor
from bittorrent import BitTorrentController

shutil.rmtree('./downloads')


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().info('Starting test...')

torrentFile = 'test/resources/debian-9.9.0-amd64-netinst.iso.torrent'
controller = BitTorrentController.createFromTorrentFile(torrentFile, 
                                                        './downloads',
                                                        reactor)

controller.torrentContext.peerId = binascii.a2b_hex('87cc700d406ca6dbcdbfdc46ea730cd64961421c')

controller.start()

def signal_handler(signo, frame):
    print('Signal received: ', signo)
    if signo == signal.SIGTERM:
        reactor.stop()

signal.signal(signal.SIGTERM, signal_handler)
reactor.run()