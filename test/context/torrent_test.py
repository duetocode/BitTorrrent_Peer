from bittorrent.context import TorrentContext
from test.utils import *
import binascii


def test_create_from_file():
    actual = TorrentContext.createFromFile(simple_file_torrent)

    assert hasattr(actual, 'infoHash')
    assert actual.infoHash == binascii.a2b_hex(simple_file_torrent_info_hash)