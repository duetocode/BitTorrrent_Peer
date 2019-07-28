from bittorrent.context import TorrentContext
from test.utils import *
import binascii


def test_create_from_file():
    actual = TorrentContext.createFromFile(simple_file_torrent)

    assert hasattr(actual, 'infoHash')
    assert actual.infoHash == binascii.a2b_hex(simple_file_torrent_info_hash)
    assert hasattr(actual, 'pieces')
    assert len(actual.pieces) > 0
    assert hasattr(actual, 'files')
    assert len(actual.files) == 1
    assert actual.files[0].length == 306184192
    assert actual.files[0].name == 'debian-9.9.0-amd64-netinst.iso'
    assert actual.files[0].path == []