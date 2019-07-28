from types import SimpleNamespace
from bittorrent.controller import ConnectionScheduler
from bittorrent.context import PeerInfo, Endpoint

def test_peerDiscovered():
    
    scheduler = ConnectionScheduler(None)

    mockPeerList = [
        PeerInfo(id=b'peer-001', endpoint=Endpoint('1.2.3.4', 2324)),
        PeerInfo(id=None, endpoint=Endpoint('5.6.7.8', 2325))
    ]

    scheduler.peerDiscovered(mockPeerList)

    assert len(scheduler.knownPeers) == 3
    assert b'peer-001' in scheduler.knownPeers
    assert Endpoint('5.6.7.8', 2325) in scheduler.knownPeers
    assert Endpoint('1.2.3.4', 2324) in scheduler.knownPeers
    assert mockPeerList[0].lastSeen is not None
    assert mockPeerList[1].lastSeen is not None

    scheduler.peerDiscovered([PeerInfo(id=b'peer-002', endpoint=Endpoint('5.6.7.8', 2325))])

    assert b'peer-002' in scheduler.knownPeers
    assert b'peer-002' == scheduler.knownPeers[Endpoint('5.6.7.8', 2325)].id
