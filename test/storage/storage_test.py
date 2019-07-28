import pytest
from pathlib import Path
import os
import hashlib
from types import SimpleNamespace
from bittorrent.storage import Storage
from bittorrent.context import TorrentContext
from test.utils import *



def test_start(multipleFilesContext, tmpdir):
    storage = Storage(multipleFilesContext, None)
    storage.start()

    assertDir = lambda p: p.exists() and p.is_dir()
    assertFile = lambda p: p.exists() and p.is_file()

    assert assertDir(Path(multipleFilesContext.home))
    assert assertFile(Path(multipleFilesContext.home, 'a.txt'))
    assert assertFile(Path(multipleFilesContext.home, 'b.txt'))
    assert assertFile(Path(multipleFilesContext.home, 'c.txt'))
    assert assertFile(Path(multipleFilesContext.home, 'debian-9.9.0-amd64-netinst.iso'))

def test_save_piece(multipleFilesContext, tmpdir):
    pieceInfo = multipleFilesContext.pieces[0]
    pieceLength = multipleFilesContext.torrentInfo.info['piece length']
    assert pieceLength > 0 and pieceLength % 32 == 0

    pieces = multipleFilesContext.pieces
    files = multipleFilesContext.files

    testData = os.urandom(pieceLength)
    hash = hashlib.sha1(testData).digest()
    # Modify the hash of the piece under testing
    pieceInfo.hash = hash

    actualDownloadedPieceIndex = -1
    def pieceDownloaded(index):
        nonlocal actualDownloadedPieceIndex
        actualDownloadedPieceIndex = index

    storage = Storage(multipleFilesContext, SimpleNamespace(pieceDownloaded=pieceDownloaded))
    storage.start()

    # Write data block by block
    for i in range(0, pieceLength, 32):
        storage.savePiece(0, i, testData[i:i+32])
    
    # check the data    
    assert actualDownloadedPieceIndex == 0
    actualData = readData(Path(multipleFilesContext.home, *files[0].path, files[0].name), 0, 7)
    assert actualData == testData[:7]
    actualData = readData(Path(multipleFilesContext.home, *files[1].path, files[1].name), 0, 7)
    assert actualData == testData[7:14]
    actualData = readData(Path(multipleFilesContext.home, *files[2].path, files[2].name), 0, 11)
    assert actualData == testData[14:25]
    actualData = readData(Path(multipleFilesContext.home, *files[3].path, files[3].name), 0, pieceLength-25)
    assert actualData == testData[25:]

    # Write to the second piece
    multipleFilesContext.pieces[1].hash = hash
    actualDownloadedPieceIndex = -1
    for i in range(0, pieceLength, 32):
        storage.savePiece(1, i, testData[i:i+32])

    assert actualDownloadedPieceIndex == 1
    actualData = readData(Path(multipleFilesContext.home, *files[3].path, files[3].name), pieceLength - 25, pieceLength * 2 - 25)
    assert actualData == testData
    

def readData(file, offset, limit):
    with open(file, 'rb') as fd:
        fd.seek(offset)
        return fd.read(limit - offset)


@pytest.fixture()
def multipleFilesContext(tmpdir):
    multipleFilesContext = TorrentContext.createFromFile(multiple_files_torrent)    
    multipleFilesContext.home = Path(tmpdir, 'library')

    return multipleFilesContext