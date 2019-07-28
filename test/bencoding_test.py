import pytest
from bittorrent.bencoding import *
from test.utils import *

def testDecodeInteger():
    buf = ByteStringBuffer(b'i12345e')
    actual = decodeInteger(buf)

    assert actual == 12345

def testDecodeByteString():
    buf = ByteStringBuffer(b'5:Hello')

    actual = decodeByteString(buf)

    assert actual == b'Hello'

def testDecodeByteStringWithExccededLength():
    buf = ByteStringBuffer(b'5:Hello World')

    actual = decodeByteString(buf)

    assert actual == b'Hello'

def test_ByteStringBuffer_popTo():
    buf = ByteStringBuffer(b'5:Hello')
    actual = buf.popTo(ord(':'))
    assert actual == b'5'

def test_decode_list():
    buf = ByteStringBuffer(b'li36ei78e3:ABCe')
    actual = decodeList(buf)

    assert actual is not None
    assert type(actual) == list
    assert len(actual) == 3
    assert actual == [36, 78, b'ABC']

def test_decode_dict():
    buf = ByteStringBuffer(b'd1:ai12e1:bi78ee')
    actual = decodeDict(buf)

    assert actual is not None
    assert type(actual) == Bulk
    assert actual['a'] == 12
    assert actual['b'] == 78
    assert actual['_range'] == (16, 0)
def test_decode_torrent_file():
    buf = ByteStringBuffer(load_file(multiple_files_torrent))

    actual = decode(buf)

    assert actual is not None
    assert type(actual) == Bulk
    assert 'info' in actual
    assert 'files' in actual['info']
    assert actual.info.name == b'multiple-files'

def testBulk():
    bulk = Bulk()
    bulk['name'] = 'Leon'

    assert bulk.name == 'Leon'
    assert 'name' in bulk


@pytest.mark.parametrize('key, expectedKey', [
    pytest.param('a b 1', 'aB1'),
    pytest.param('a  b   1', 'aB1'),
    pytest.param('a_b_1', 'aB1'),
    pytest.param('a__b___1', 'aB1'),
    pytest.param('a-b-1', 'aB1'),
    pytest.param('a--b---1', 'aB1'),
    pytest.param('a-b c_d f 1', 'aBCDF1')
])
def test_key_normalization(key, expectedKey):
    bulk = Bulk()
    bulk[key] = 'abc'
    
    actual = Bulk.keyNormalized(bulk)

    assert getattr(actual, expectedKey) == 'abc'
    
