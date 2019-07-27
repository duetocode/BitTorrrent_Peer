from bittorrent.bencoding import decode, Bulk        

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
        torrentInfo = decode(_load(file))
        if not isValidTorrent(torrentInfo):
            raise InvalidTorrentFileError(torrentInfo)

        torrentContext = TorrentContext()
        torrentContext.torrentInfo = torrentInfo
        return torrentContext

    def isSingleFile(self):
        return 'files' not in self.torrentInfo.info

class InvalidTorrentFileError(Exception):
    
    def __init__(self, torrentInfo):
        self.torrentInfo = torrentInfo
        super().__init__()

def isValidTorrent(torrentInfo:Bulk) -> bool:
    result = torrentInfo.assertAttribute('info', Bulk) \
                and torrentInfo.assertAttribute('announce', bytes) \
                and torrentInfo.info.assertAttribute('piece length', int) \
                and torrentInfo.info.assertAttribute('pieces', list) \
                and torrentInfo.info.assertAttribute('name', bytes) \
                and (torrentInfo.info.assertAttribute('length', int) \
                    or torrentInfo.info.assertAttribute('files', list))

    return result
