import logging
import struct
from twisted.internet.protocol import Protocol

from .handshake_state import HandshakeState
from .connected_state import ConnectedState
from bittorrent.context import TorrentContext

LENGTH_HEADER = 4
LENGTH_LIMIT = 1024 * 1024 * 8

class BitTorrentProtocol(Protocol):

    states = [HandshakeState, ConnectedState]

    def __init__(self, 
                 torrentContext:TorrentContext,
                 protocolDelegation,
                 messageHandler,
                 peerInfo=None, 
                 initiator=False,
                 initiateState=None):
        self.torrentContext = torrentContext
        self.delegation = protocolDelegation
        self.initiator = initiator
        self.peerInfo = peerInfo
        self.stateList = list(reversed(BitTorrentProtocol.states))
        self.messageHandler = messageHandler
        if initiateState is None:
            self.state = self._nextState()
        else:
            self.state = initiateState
        self.buf = b''
        self.expectedLength = None
        self.logger = logging.getLogger('protocol')

    def sendMessage(self, message):
        """commit message to protocol"""
        self.transport.write(message.toBytes())

    def shutdown(self):
        self.transport.loseConnection()

    def packetReceived(self, packet):
        nextState = self.state.packetReceived(packet)
        if nextState:
            self.logger.debug('Swith to next protocol state. %s', self.peerInfo.endpoint)
            oldState = self.state
            self.state = self._nextState()
            # We see the transition from handshake to connected as peer-connected event. 
            if type(self.state) == ConnectedState and type(oldState) == HandshakeState:
                self.delegation.peerConnected(self)

    # -- overrides --
    def connectionMade(self):
        # We do not invoke peerConnected if this callback, 
        # since we only consider it is connected after a successful handshake
        self.state.connectionMade()

    def connectionLost(self, reason):
        self.delegation.peerDisconnected(self)

    def dataReceived(self, data):
        self.buf += data

        # Process until there is not enough data left in the buffer
        while len(self.buf) >= self._calculateExpectedLength():
            if self.expectedLength is None:
                # We do not have expectedLength, which means we are still reading the prefixed length
                self.lengthDataReceived()
            else:
                # We got enough data for the payload
                self.payloadReceived()

    # -- Data handling --
    def lengthDataReceived(self):
        # Double check
        if len(self.buf) < LENGTH_HEADER:
            return
        
        # Decode the data
        self.expectedLength = struct.unpack('!I', self.buf[:LENGTH_HEADER])[0]

        # Ensure the length of the expected data is not negative or too large
        if self.expectedLength < 0 or self.expectedLength > LENGTH_LIMIT:
            self.transport.loseConnection()

        # Remove the decoded data from buffer
        self.buf = self.buf[LENGTH_HEADER:]

    def payloadReceived(self):
        # Check the length of the data
        if len(self.buf) < self.expectedLength:
            return
        
        # Move the payload out from buffer
        payload = self.buf[:self.expectedLength]
        self.buf = self.buf[self.expectedLength:]

        # Process the payload
        self.packetReceived(payload)

        # Switch back to the length reading state
        self.expectedLength = None


    def _calculateExpectedLength(self):
        if self.expectedLength is None:
            return LENGTH_HEADER
        else:
            return self.expectedLength

    def _nextState(self):
        state = self.stateList.pop()(self)
        return state
