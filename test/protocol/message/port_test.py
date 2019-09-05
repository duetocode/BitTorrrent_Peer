from bittorrent.protocol.message import Port

def test_parse():
    actual = Port.parse(b'\x04\x00')
    assert actual is not None
    assert actual.port == 1024

def test_serialize():
    port = Port(port=2048)
    
    actual = port.serialize()

    assert actual is not None
    assert actual == b'\x08\x00'