import logging

HEADER = b'\x13BitTorrent protocol'
EXPECTED_MESSAGE_LENGTH = 20 + 8 + 20 + 20

class HandshakeState:

    def __init__(self, protocol):
        self.protocol = protocol
        self.logger = logging.getLogger(f'protocol.HandshakeState')

    def connectionMade(self):
        self.protocol.expectedLength = EXPECTED_MESSAGE_LENGTH
        if self.protocol.initiator == True:
            self.sendHandshakeMessage()

    @property
    def expectedLength(self):
        return EXPECTED_MESSAGE_LENGTH

    def packetReceived(self, packet):
        assert len(packet) == EXPECTED_MESSAGE_LENGTH

        # Check protocol header
        if packet[:len(HEADER)] != HEADER:
            self.protocol.transport.loseConnection()
            return False

        # save features
        self.protocol.peerInfo.features = packet[20:28]

        # Check info hash
        if self.protocol.torrentContext.infoHash != packet[28:48]:
            self.protocol.transport.loseConnection()
            return False
        
        # Check peer id
        peerId = packet[48:68]
        if self.protocol.peerInfo.id is not None:
            if self.protocol.peerInfo.id != peerId:
                self.protocol.transport.loseConnection()
                return False
        else:
            # Save the peer id if we do not have one
            self.protocol.peerInfo.id = peerId

        # Send back handshake message if we are not the initiator
        if not self.protocol.initiator:
            self.sendHandshakeMessage()

        return True

    def sendHandshakeMessage(self):
        transport = self.protocol.transport
        transport.write(HEADER)
        transport.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')
        transport.write(self.protocol.torrentContext.infoHash)
        transport.write(self.protocol.torrentContext.peerId)
        self.logger.debug('Handshake message sent.')
        