from urllib import request
from urllib.parse import urlencode
import logging
import socket
import struct
import threading
import ipaddress

from bittorrent.context import TorrentContext, PeerInfo, Endpoint
from bittorrent.bencoding import decode, ByteStringBuffer

class PeerDiscovery:
    """
    Service that responsible for discovering new peers.
    It updates the knownPeers attribute of the context when it finds new peers
    and publishes messages to notify the system about this event."""

    def __init__(self, ctx: TorrentContext, delegation):
        self.ctx = ctx
        self.trackerId = None
        self.delegation = delegation
        self.timer = None
        self.logger = logging.getLogger('PeerDiscovery')

    def start(self):
        self._schedule(0.1)
        self.logger.info('Peer discovery started.')

    def shutdown(self):
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None

    def _schedule(self, interval=30):
        self.timer = threading.Timer(interval, lambda: self._scrape())
        self.timer.start()

    def _scrape(self):
        self.logger.info('Scrape infomation of peers from tracker.')
        # Request peer list from tracker
        response = self._request()
        if response is None:
            self.logger.info('Empty response from tracker.')
            return

        if hasattr(response, 'tracker_id'):
            self.logger.debug('Tracker ID: %s', response.tracker_id)
            self.trackerId = response.tracker_id

        # Transform peer list into List[PeerInfo]
        self.delegation.peerDiscovered(self._transform(response.peers))

        # Set timer for the next scraping
        if self.timer is not None:
            interval = 30
            if hasattr(response, 'interval'):
                try:
                    interval = int(response.interval)
                except:
                    pass

            self.logger.info('Next scraping will be in %d seconds.', interval)
            self._schedule(interval)

    def _transform(self, peers):
        result = None

        if type(peers) is list:
            return map(_mapPeerInfo, peers)
        else:
            if len(peers) % 6 != 0:
                self.logger.warning('Invalid peers string.')
                return 0
            return [_mapCompactedPeerInfo(peers[i : i+6]) for i in range(0, len(peers), 6)]

    def _request(self):
        assert hasattr(self.ctx.torrentInfo, 'announce')
        params = {
            'info_hash': self.ctx.infoHash,
            'peer_id': self.ctx.peerId,
            'port': self.ctx.port,
            'uploaded': 0,
            'downloaded': 0,
            'left': self.ctx.length,
            'event': 'started',
            'compact': 1}
        if self.trackerId is not None:
            params['trackerid'] = self.trackerId

        url = '%s?%s' % (self.ctx.torrentInfo.announce.decode(), urlencode(params))
        self.logger.debug('Requesting tracker: %s', url)

        req = request.Request(url=url, headers={'User-Agent': 'BitTorrentHunter-1.0.0'})
        with request.urlopen(req) as res:
            if res.status != 200:
                self.logger.warning('Failed to scape peers from tracker: %s State: %d %s',
                    self.ctx.torrentInfo.announce,
                    res.status,
                    res.reason)
                return None
            else:
                data = res.read()
                res = decode(ByteStringBuffer(data))

                if hasattr(res, 'failure_reason'):
                    self.logger.warning('Failed to scrape peers from tracker: %s', res.failure_reason)
                    return None

                if hasattr(res, 'warning_message'):
                    self.logger.warning('Received a warning message: %s', res.warning_message)
                return res


def _mapPeerInfo(info):
    key = (info.ip, info.port)
    return key, PeerInfo(peerId=info.peer_id, endpoint=Endpoint(info.ip, info.port))

def _mapCompactedPeerInfo(info):
    host = struct.unpack('!I', info[:4])[0]
    host = str(ipaddress.IPv4Address(host))
    port = struct.unpack('!H', info[4:6])[0]

    return PeerInfo(endpoint=Endpoint(host, port))