from bittorrent.protocol.message import Bitfield
from bittorrent.peer_info import PeerInfo
import logging
from time import time
from twisted.internet import task
import random

class ConnectionScheduler:

    def __init__(self, connectionSchedulerDelegation):
        self.logger = logging.getLogger('controller.ConnectionScheduler')
        self.delegation = connectionSchedulerDelegation
        self.knownPeers = {}
        self.connections = {}
        self.running=False

    def start(self):
        self.running = True
        self.loopingCall = task.LoopingCall(self._patrol)
        self.loopingCall.start(1.0)

    def shutdown(self):
        # Stop patrol loop
        if self.loopingCall is not None:
            self.loopingCall.stop()
            self.loopingCall = None
        self.running = False

        # Close all connections
        for _, protocol in self.connections.items():
            protocol.shutdown()

    def _patrol(self):
        # filter out connected peers from known peers list
        candidates = [p for p in self.knownPeers.values if p.endpoint not in self.connections]
        if len(candidates) == 0:
            self.logger.info('No peers to schedule')
            return
        
        logger.info('Found %d peers to schedule new connection.', len(candidates))

        # sort
        candidates = sorted(candidates, key=lambda c: [c.lastSeen, c.id is not None], reverse=True)

        # Sample a candidate
        peerInfo = candidates[random.randint(0, len(candidates) - 1)]

        # initiate the connection
        self.connections[peerInfo.endpoint] = self.delegation.initiateNewConnection(peerInfo)


    # -- ProtocolDelegation --
    def peerConnected(self, protocol):
        # update peer info
        peerInfo = self.knownPeers.get(protocol.peerInfo.endpoint)
        if peerInfo is not None:
            peerInfo.id = protocol.peerInfo.id
        else:
            self.peerDiscovered([peerInfo])

        # report our download progress by sending bitfield message
        bitfieldMessage = Bitfield(self.delegation.torrentContext.pieces)
        protocol.sendMessage(bitfieldMessage)

    def peerDisconnected(self, protocol):
        # remove from connections map
        peerInfo = protocol.peerInfo
        if peerInfo.endpoint in self.connections:
            del self.connections[peerInfo.endpoint]
            

    # -- DiscoveryDelegation -- 
    def peerDiscovered(self, peerInfoList:List[PeerInfo]):
        for peerInfo in peerInfoList:
            if peerInfo.id is not None and peerInfo.id not in self.knownPeers:
                self.knownPeers[peerInfo.id] == peerInfo

            if peerInfo.endpoint not in self.knownPeers or peerInfo.id != self.knownPeers[peerInfo.endpoint]:
                self.knownPeers[peerInfo.endpoint] = peerInfo
            peerInfo.lastSeen = time()
                    

