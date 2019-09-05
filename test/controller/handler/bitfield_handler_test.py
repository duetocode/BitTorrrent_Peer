from types import SimpleNamespace
from bittorrent.controller.handler import BitfieldHandler


def test_bitfield_message_received():
    handler = BitfieldHandler(None)
    message = SimpleNamespace(array=[])
    protocol = SimpleNamespace(peerInfo=SimpleNamespace())

    handler.messageReceived(message, protocol)

    assert hasattr(protocol.peerInfo, 'pieces')
    assert protocol.peerInfo.pieces == message.array

