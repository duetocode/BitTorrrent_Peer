import logging
from .handler import *
from bittorrent.protocol.message import *

class MessageHandler:

    def __init__(self, torrentContext):
        self.torrentContext = torrentContext
        self.handlers = [
            ChokeHandler(torrentContext), 
            UnchokeHandler(torrentContext),
            None,
            None,
            None,
            BitfieldHandler(torrentContext)
        ]
        self.logger = logging.getLogger('controller.message.handler')
        

    def messageReceived(self, message:Message, protocol):
        handler = None
        if message.id >= 0 and message.id < len(self.handlers):
            handler = self.handlers.get(message.id)

        if handler is not None:
            # Pass the message to actual handler
            handler.messageReceived(message, protocol)
        else:
            logger.debug('Not handler found for message with id %d', message.id)