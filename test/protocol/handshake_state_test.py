import pytest
from types import SimpleNamespace
from hashlib import sha1
from io import BytesIO

from bittorrent.protocol.handshake_state import HandshakeState
from bittorrent.context import PeerInfo, Endpoint

def test_initiate(state:HandshakeState):
    state.connectionMade()
    _check_message_sended(state)

def test_receive_handshake(state:HandshakeState):
    remotePeerId = sha1(b'REMOTE_ID').digest()
    state.protocol.initiator = False

    state.connectionMade()
    assert state.protocol.expectedLength == 20 + 8 + 20 + 20

    result = state.packetReceived(b'\x13BitTorrent protocol' 
        + b'\x00' * 8 
        + state.protocol.torrentContext.infoHash 
        + remotePeerId)
    
    assert result == True
    assert state.protocol.peerInfo.id == remotePeerId

    _check_message_sended(state)


@pytest.fixture
def state():
    transport = BytesIO()
    transport.loseConnection = transport.close

    peerId = sha1(b'PEER_ID').digest()
    
    infoHash = sha1(b'INFO_HASH').digest()

    protocol = SimpleNamespace(
        torrentContext=SimpleNamespace(
            peerId=peerId,
            infoHash=infoHash,
        ),
        transport=transport,
        initiator=True,
        peerInfo=PeerInfo(id=None, endpoint=None)
    )

    state = HandshakeState(protocol)

    return state

def _check_message_sended(state:HandshakeState):
    message = state.protocol.transport.getvalue()

    assert len(message) == 20 + 8 + 20 + 20
    assert message[:20] == b'\x13BitTorrent protocol'
    assert message[20:28] == b'\0' * 8
    assert message[28:48] == state.protocol.torrentContext.infoHash
    assert message[48:68] == state.protocol.torrentContext.peerId
