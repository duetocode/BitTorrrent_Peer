from types import SimpleNamespace
from bittorrent.discovery import PeerDiscovery

def test_tracker_discovery(singleFileContext):
    actual = None
    def peerDiscovered(peers):
        nonlocal actual
        actual = peers

    discovery = PeerDiscovery(singleFileContext, SimpleNamespace(peerDiscovered=peerDiscovered))

    discovery._scrape()

    assert actual is not None and isinstance(actual, list)

    if len(actual) > 0:
        for peerInfo in actual:
            assert peerInfo.endpoint is not None
            assert peerInfo.endpoint.host is not None and len(peerInfo.endpoint.host) > 7
            assert peerInfo.endpoint.port is not None and type(peerInfo.endpoint.port) == int
