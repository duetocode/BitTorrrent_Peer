import logging
from .message import parse

class ConnectedState:

    def __init__(self, protocol):
        self.protocol = protocol
        self.logger = logging.getLogger('protocol.ConnectedState')

    def packetReceived(self, packet):
        if packet is None or len(packet) < 1:
            self.logger.debug('Empty packet ignored %s', packet if packet is not None else 'None')
            return False
            
        # Locate handler
        message = parse(packet)

        if message is not None:
            self.protocol.messageHandler.messageReceived(message, protocol)
        else:
            self.logger.debug('Unknown message with type %d ignored', packet[0])

        return False