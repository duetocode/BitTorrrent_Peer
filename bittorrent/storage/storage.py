import logging
from pathlib import Path
from hashlib import sha1
from mmap import mmap
from bittorrent.context import PieceInfo, PieceState

class Storage:

    def __init__(self, torrentContext, delegation):
        self.torrentContext = torrentContext
        self._fd = []
        self.root = Path(torrentContext.root)
        self.logger = logging.getLogger('storage')
        self.delegation = delegation

    def savePiece(self, pieceIndex, offset, data, flush=False):
        # Verification
        if len(data) <= 0:
            self.logger.warning('Invalid data')
            return None

        buf = data
        if pieceIndex < 0 or pieceIndex >= len(self.torrentContext.pieces):
            self.logger.warning('Invalid piece index.')
            return None

        # Locate the pirce
        pieceLength = self.torrentContext.torrentInfo.info['piece length']
        pieceInfo = self.torrentContext.pieces[pieceIndex]

        if pieceInfo.state == PieceState.Have:
            # Do not write data to already downloaded piece
            return

        # locate file and offset
        fileIndex, offsetInFile = self._locateFileAndOffset(pieceIndex, offset)

        # write data into files
        while len(buf) > 0 and fileIndex < len(self.torrentContext.files):
            fileSize = self._fd[fileIndex][1].size()
            mm = self._fd[fileIndex][1]
            remainingSpace = fileSize - offsetInFile
            lengthToWrite = remainingSpace if remainingSpace < len(buf) else len(buf)
            mm[offsetInFile:offsetInFile+lengthToWrite] = buf[:lengthToWrite]
            buf = buf[lengthToWrite:]
            
            if flush:
                self._fd[fileIndex][1].flush(offsetInFile, lengthToWrite)

            fileIndex += 1
            offsetInFile = 0
        
        # report piece downloaded event
        pieceInfo.progress += len(data)
        if pieceInfo.progress >= pieceLength:
            self._pieceDownloaded(pieceIndex)

    def loadPiece(self, pieceIndex):
        pieceLength = self.torrentContext.torrentInfo.info['piece length']
        fileIndex, offsetInFile = self._locateFileAndOffset(pieceIndex, 0)

        buf = b''
        while fileIndex < len(self.torrentContext.files) and len(buf) < pieceLength:
            buf += self._fd[fileIndex][1][ offsetInFile : offsetInFile+pieceLength-len(buf) ]
            fileIndex += 1
            offsetInFile = 0

        assert len(buf) == pieceLength

        return buf    

    def isFinished(self):
        return all([p.state == PieceState.Have for p in self.torrentContext.pieces])

    def _pieceDownloaded(self, pieceIndex):
        data = self.loadPiece(pieceIndex)
        pieceInfo = self.torrentContext.pieces[pieceIndex]
        if sha1(data).digest() == pieceInfo.hash:
            pieceInfo.state = PieceState.Have
            self.delegation.pieceDownloaded(pieceIndex)
        else:
            pieceInfo.state = PieceState.NotHave

    def _locateFileAndOffset(self, pieceIndex:int, offset:int) -> (int, int):
        pieceLength = self.torrentContext.torrentInfo.info['piece length']
        globalOffset = pieceIndex * pieceLength + offset

        counter = 0
        for i, fileInfo in enumerate(self.torrentContext.files):
            end = counter + fileInfo.length
            if end >= globalOffset:
                return i, globalOffset - counter
            else:
                counter = end

        raise IndexError()

    def start(self):
        # The library directory
        if not self.root.exists():
            self.root.mkdir()
        if not self.root.is_dir():
            raise OSError('Download is not a directory.')
        self.logger.debug('Library initialized')

        # Root directory of this storage
        if self.torrentContext.isSingleFile():
            self.logger.debug('It is a single-file torrent.')
        else:
            self.logger.debug('It is a multiple-files torrent.')

        # Open all files
        for fileInfo in self.torrentContext.files:
            file = Path(self.root, *fileInfo.path, fileInfo.name)
            # Create the file if not exists
            if not file.exists():
                with open(file, 'wb') as fd:
                    if fileInfo.length > 0:
                        fd.seek(fileInfo.length - 1)
                        fd.write(b'\0')
            fd = open(file, 'r+b')
            self._fd.append((fd, mmap(fd.fileno(), 0)))
            self.logger.info('File %s has been created.', fileInfo.name)

    def shutdown(self):
        for fd in self._fd:
            fd[1].close()
            fd[0].close()
