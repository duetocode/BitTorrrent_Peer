import pytest
from types import SimpleNamespace
from typing import List
from bittorrent.controller import ConnectionScheduler
from bittorrent.context import PeerInfo, Endpoint

def test_peerDiscovered(scheduler:ConnectionScheduler, mockPeerList:List[PeerInfo]):

    scheduler.peerDiscovered(mockPeerList)

    assert len(scheduler.knownPeers) == 3
    assert len(set([p.endpoint for p in scheduler.knownPeers.values()])) == 2
    assert b'peer-001' in scheduler.knownPeers
    assert Endpoint('5.6.7.8', 2325) in scheduler.knownPeers
    assert Endpoint('1.2.3.4', 2324) in scheduler.knownPeers
    assert mockPeerList[0].lastSeen is not None
    assert mockPeerList[1].lastSeen is not None

    scheduler.peerDiscovered([PeerInfo(id=b'peer-002', endpoint=Endpoint('5.6.7.8', 2325))])

    assert b'peer-002' in scheduler.knownPeers
    assert b'peer-002' == scheduler.knownPeers[Endpoint('5.6.7.8', 2325)].id
    assert len(set([p.endpoint for p in scheduler.knownPeers.values()])) == 2

    mockPeerList.append(PeerInfo(id=None, endpoint=Endpoint('9.8.7.6', 2455)))
    scheduler.peerDiscovered(mockPeerList)
    assert len(set([p.endpoint for p in scheduler.knownPeers.values()])) == 3

def test_peer_disconnected(scheduler:ConnectionScheduler, mockPeerList:List[PeerInfo]):
    peerInfo = mockPeerList[0]
    protocol = SimpleNamespace(peerInfo=peerInfo)
    scheduler.connections[peerInfo.endpoint] = protocol

    scheduler.peerDisconnected(protocol)

    assert len(scheduler.connections) == 0

def test_unkown_peer_connected(scheduler:ConnectionScheduler, mockPeerList):
    actualMessage = None
    def sendMessage(msg):
        nonlocal actualMessage
        actualMessage = msg
    discoveredPeers = None
    def peerDiscovered(peers):
        nonlocal discoveredPeers
        discoveredPeers = peers

    peerInfo = mockPeerList[0]
    pieces = ['PIECE']
    scheduler.peerDiscovered = peerDiscovered

    scheduler.delegation = SimpleNamespace(pieces=pieces)
    protocol = SimpleNamespace(sendMessage=sendMessage, peerInfo=peerInfo)
    
    scheduler.peerConnected(protocol)

    assert discoveredPeers is not None and discoveredPeers[0] is peerInfo
    assert actualMessage is not None and actualMessage.pieces is pieces

def test_known_peer_connected(scheduler:ConnectionScheduler, mockPeerList):
    actualMessage = None
    def sendMessage(msg):
        nonlocal actualMessage
        actualMessage = msg
    peerInfo = mockPeerList[0]
    pieces = ['PIECE']
    knownPeer = PeerInfo(endpoint=peerInfo.endpoint)
    scheduler.knownPeers[knownPeer.endpoint] = knownPeer

    scheduler.delegation = SimpleNamespace(pieces=pieces)
    protocol = SimpleNamespace(sendMessage=sendMessage, peerInfo=peerInfo)

    scheduler.peerConnected(protocol)

    assert knownPeer.id is not None
    assert actualMessage is not None
    
def test_patrol(scheduler, mockPeerList):
    # Setup
    for peerInfo in mockPeerList:
        scheduler.knownPeers[peerInfo.endpoint] = peerInfo
        if peerInfo.id is not None:
            scheduler.knownPeers[peerInfo.id] = peerInfo

    selectedPeerInfo = None
    def initiateNewConnection(peerInfo):
        nonlocal selectedPeerInfo
        selectedPeerInfo = peerInfo
    scheduler.delegation = SimpleNamespace(initiateNewConnection=initiateNewConnection)

    # Run
    scheduler._patrol()

    # Assert
    assert selectedPeerInfo is not None
    assert selectedPeerInfo.endpoint in [p.endpoint for p in mockPeerList]

def test_patrol_with_empty_cadidates_list(scheduler):
    scheduler._patrol()
    # nothing hanppends

@pytest.fixture()
def scheduler():
    return ConnectionScheduler(None)

@pytest.fixture()
def mockPeerList():
    return [
        PeerInfo(id=b'peer-001', endpoint=Endpoint('1.2.3.4', 2324)),
        PeerInfo(id=None, endpoint=Endpoint('5.6.7.8', 2325))
    ]