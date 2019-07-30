import pytest
from types import SimpleNamespace

from bittorrent.controller import MessageHandler

def test_message_received(handler):
    mockMessage = SimpleNamespace(id=0)
    protocol = SimpleNamespace()

    handler.messageReceived(mockMessage, protocol)
    assert len(handler.handlers[0].messages) == 1

    actualMessage, actualProtocol = handler.handlers[0].messages.pop()
    assert actualMessage == mockMessage
    assert actualProtocol == protocol

def test_unknown_type_message_received(handler):
    mockMessage = SimpleNamespace(id=100)
    protocol = SimpleNamespace()

    handler.messageReceived(mockMessage, protocol)
    assert len(handler.handlers[0].messages) == 0


@pytest.fixture()
def handler(singleFileContext):
    handler = MessageHandler(singleFileContext, [MockMessageHandler()])
    return handler

class MockMessageHandler:
    
    def __init__(self):
        self.messages = []

    def messageReceived(self, message, protocol):
        self.messages.append((message, protocol))
