from bittorrent.context import Endpoint

def test_eq():
    a = Endpoint('12.32.4.21', 2324)
    b = Endpoint('12.32.4.21', 2324)

    assert a == b

    b.port = 2325
    assert a != b

    b.port = 2324
    b.host = '12.32.4.22'
    assert a != b

def test_hash():
    a = Endpoint('12.32.4.21', 2324)
    b = Endpoint('12.32.4.21', 2324)

    assert hash(a) == hash(b)

    b.port = 2325
    assert hash(a) != hash(b)

    b.port = 2324
    b.host = '12.32.4.22'
    assert hash(a) != hash(b)
