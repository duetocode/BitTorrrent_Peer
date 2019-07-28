import hashlib
from typing import List
from bittorrent.bencoding import decode, Bulk, ByteStringBuffer
from .piece_info import PieceInfo
from .file_info import FileInfo


def _load(file) -> bytes:
    with open(file, 'rb') as fd:
        return fd.read()        

class TorrentContext:

    def __init__(self):
        self.peerId = None
        self.torrentInfo = None
        self.pieces = []
        self.files = []
        self.home = None
        self.knownPeers = []
        self.connectedPeers = {}

    @classmethod
    def createFromFile(clz, file):
        rawData = _load(file)
        torrentInfo = decode(ByteStringBuffer(rawData))
        if not isValidTorrent(torrentInfo):
            raise InvalidTorrentFileError(torrentInfo)

        torrentContext = TorrentContext()
        torrentContext.torrentInfo = torrentInfo

        # calculate info hash
        torrentContext.infoHash = calculateInfoHash(torrentInfo, rawData)

        # calculate piece list
        torrentContext.pieces = _buildPieceList(torrentInfo)

        # calculate file lists
        torrentContext.files = _buildFileList(torrentContext)
        return torrentContext

    def isSingleFile(self):
        return 'files' not in self.torrentInfo.info

class InvalidTorrentFileError(Exception):
    
    def __init__(self, torrentInfo):
        self.torrentInfo = torrentInfo
        super().__init__()

def isValidTorrent(torrentInfo:Bulk) -> bool:
    result = assertAttribute(torrentInfo, 'info', Bulk) \
                and assertAttribute(torrentInfo, 'announce', bytes) \
                and assertAttribute(torrentInfo.info, 'piece length', int) \
                and assertAttribute(torrentInfo.info, 'pieces', bytes) \
                and len(torrentInfo.info.pieces) % 20 == 0 \
                and assertAttribute(torrentInfo.info, 'name', bytes) \
                and (assertAttribute(torrentInfo.info, 'length', int) \
                    or assertAttribute(torrentInfo.info, 'files', list))

    return result

def calculateInfoHash(torrentInfo:Bulk, rawData:bytes) -> bytes:
    range = torrentInfo.info['_range']
    length = len(rawData)
    return hashlib.sha1(rawData[length - range[0]:length - range[1]]).digest()

def _buildPieceList(torrentInfo:Bulk) -> List[PieceInfo]:
    pieces = torrentInfo.info.pieces
    assert len(pieces) % 20 == 0
    
    result = []

    for i in range(0, len(pieces), 20):
        hash = pieces[i:i+20]
        result.append(PieceInfo(index=i, hash=hash))

    return result

def _buildFileList(torrentContext:TorrentContext) -> List[FileInfo]:
    fileList = []
    info = torrentContext.torrentInfo.info
    if torrentContext.isSingleFile():
        fileInfo = FileInfo(name=info.name.decode('utf-8'), 
                            path=[],
                            length=info.length)
        fileList.append(fileInfo)
    else:
        for file in info.files:
            fileInfo = FileInfo(name=file.path[-1].decode('utf-8'),
                                path=file.path[:-1],
                                length=file.length)
            fileList.append(fileInfo)
    
    return fileList

def assertAttribute(self, name, type):
    return name in self and isinstance(self[name], type)