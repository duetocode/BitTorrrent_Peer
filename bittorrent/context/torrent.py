from bittorrent.bencoding import decode, Bulk, ByteStringBuffer
import hashlib

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
    def createFromFile(self, file):
        rawData = _load(file)
        torrentInfo = decode(ByteStringBuffer(rawData))
        if not isValidTorrent(torrentInfo):
            raise InvalidTorrentFileError(torrentInfo)

        torrentContext = TorrentContext()
        torrentContext.torrentInfo = torrentInfo

        # calculate info hash
        self.infoHash = calculateInfoHash(torrentInfo, rawData)
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
                and assertAttribute(torrentInfo.info, 'name', bytes) \
                and (assertAttribute(torrentInfo.info, 'length', int) \
                    or assertAttribute(torrentInfo.info, 'files', list))

    return result

def calculateInfoHash(torrentInfo:Bulk, rawData:bytes) -> bytes:
    range = torrentInfo.info['_range']
    length = len(rawData)
    return hashlib.sha1(rawData[length - range[0]:length - range[1]]).digest()

def assertAttribute(self, name, type):
    return name in self and isinstance(self[name], type)