import pytest
from types import SimpleNamespace
from pathlib import Path
from bittorrent.bencoding import decode, ByteStringBuffer
from bittorrent.context import TorrentContext
from test.utils import *
from hashlib import sha1

@pytest.fixture()
def multipleFilesContext(tmpdir):
    multipleFilesContext = TorrentContext.createFromFile(multiple_files_torrent)    
    multipleFilesContext.home = Path(tmpdir, 'library')
    multipleFilesContext.host = '123.21.54.234'
    multipleFilesContext.port = 2342
    multipleFilesContext.peerId = sha1(b'bittorrent_peer').digest()

    return multipleFilesContext

@pytest.fixture
def singleFileContext(tmpdir):
    singleFilesContext = TorrentContext.createFromFile(simple_file_torrent)    
    singleFilesContext.home = Path(tmpdir, 'library')
    singleFilesContext.host = '123.21.54.234'
    singleFilesContext.port = 2342
    singleFilesContext.peerId = sha1(b'bittorrent_peer').digest()

    return singleFilesContext
