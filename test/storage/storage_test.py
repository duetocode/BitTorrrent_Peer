import pytest
from pathlib import *
from bittorrent.storage import Storage
from bittorrent.context import TorrentContext
from test.utils import *


def test_start(multipleFilesContext, tmpdir):
    multipleFilesContext.home = Path(tmpdir, 'library')

    storage = Storage(multipleFilesContext, None)
    storage.start()

    assert multipleFilesContext.home.exists()
    assert Path(multipleFilesContext.home, 'a.txt').exists()
    assert Path(multipleFilesContext.home, 'b.txt').exists()
    assert Path(multipleFilesContext.home, 'c.txt').exists()
    assert Path(multipleFilesContext.home, 'debian-9.9.0-amd64-netinst.iso').exists()

@pytest.fixture()
def multipleFilesContext():
    return TorrentContext.createFromFile(multiple_files_torrent)    