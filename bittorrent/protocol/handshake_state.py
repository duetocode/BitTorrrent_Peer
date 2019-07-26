import logging

HEADER = b'\x13BitTorrent protocol'
EXPECTED_MESSAGE_LENGTH = 20 + 8 + 20 + 20

class HandshakeState:

    def connectionMade(self, protocol):
        if protocol.initiator == True:
            self.sendHandshakeMessage(protocol)

        self.logger = logging.getLogger(f'protocol.HandshakeState')

    @property
    def expectedLength(self):
        return EXPECTED_MESSAGE_LENGTH

    def packetReceived(self, packet, protocol):
        assert len(packet) == EXPECTED_MESSAGE_LENGTH

        # Check protocol header
        if packet[:len(HEADER)] != HEADER:
            self.protocol.transport.loseConnection()
            return False

        # save features
        self.protocol.peerInfo.features = packet[20:28]

        # Check info hash
        if self.protocol.torrentContext.metaInfo.infoHash != packet[28:48]:
            self.protocol.transport.loseConnection()
            return False
        
        # Check peer id
        peerId = packet[48:68]
        if self.protocol.peerInfo.peerId is not None:
            if self.protocol.peerInfo.peerId != peerId:
                self.protocol.transport.loseConnection()
                return False
        else:
            # Save the peer id if we do not have one
            self.protocol.peerInfo.peerId = peerId

        # Send back handshake message if we are not the initiator
        if not self.protocol.initiator:
            self.sendHandshakeMessage()

        return True

    def sendHandshakeMessage(self, protocol):
        transport = self.connectionContext.transport
        transport.write(HEADER)
        transport.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')
        transport.write(self.connectionContext.torrentContext.metaInfo.infoHash)
        transport.write(self.connectionContext.torrentContext.peerId)
        self.logger.debug('Handshake message sent.')
        