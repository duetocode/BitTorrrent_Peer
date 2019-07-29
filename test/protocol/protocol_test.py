from struct import pack
from bittorrent.protocol import BitTorrentProtocol

def test_dataReceived():
    mockState = MockState(None)

    protocol = BitTorrentProtocol(None, None, initiateState=mockState)
    protocol.stateList = [MockState]

    # connection made
    protocol.connectionMade()
    assert mockState.connected == True

    data = pack('!I', 5) + b'Hello'
    protocol.dataReceived(data[:3])
    assert len(mockState.packets) == 0
    protocol.dataReceived(data[3:])
    assert len(mockState.packets) == 1
    data = pack('!I', 7) + b'Hello, ' + pack('!I', 6) + b'World!' + pack('!I', 4) + b'next'
    protocol.dataReceived(data[:5])
    assert len(mockState.packets) == 1
    protocol.dataReceived(data[5:])
    assert len(mockState.packets) == 3
    assert protocol.state.id == 1
    assert protocol.state.packets[0] == b'next'
    assert len(protocol.state.packets) == 1
    
class MockState:

    counter = 0

    def __init__(self, protocol):
        self.connected = False
        self.packets = []
        self.id = MockState.counter
        self.protocol = protocol
        MockState.counter += 1
        
    def connectionMade(self):
        self.connected = True

    def packetReceived(self, packet):
        self.packets.append(packet)
        return len(self.packets) >= 3
