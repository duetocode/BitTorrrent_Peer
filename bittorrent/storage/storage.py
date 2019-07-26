import logging
from pathlib import Path
from hashlib import sha1

from bittorrent import PieceState, PieceInfo

class Storage:

    def __init__(self, torrentContext, delegation):
        self.torrentContext = torrentContext
        self.ctx = ctx
        self._fd = []
        self.library = Path(library)
        self.logger = logging.getLogger('storage')
        self.delegation = delegation

    def savePiece(self, pieceIndex, offset, data, flush=False):
        if len(data) <= 0:
            logger.warning('Invalid data')
            return None

        buf = data
        if pieceIndex < 0 or pieceIndex >= len(self.torrentContext.pieces):
            logger.warning('Invalid piece index.')
            return None

        pieceInfo = self.torrentContext.pieces[pieceIndex]

        # locate file and offset
        fileIndex, offsetInFile = self.torrentContext.locateFileAndOffset(pieceIndex)
        offsetInFile += offset

        # write data into files
        while len(buf) > 0 and fileIndex < len(self.torrentContext.files):
            fileSize = self._fd[fileIndex][1].size()
            mm = self._fd[fileIndex][1]
            remainingSpace = fileSize - offsetInFile
            lengthToWrite = remainingSpace if remainingSpace < len(buf) else len(buf)
            mm[offsetInFile:offsetInFile+lengthToWrite] = buf[:lengthToWrite]
            buf = buf[lengthToWrite:]
            
            if offsetInFile+lengthToWrite == fileSize and self.verify(fileIndex):
                self._fileDownloaded(fileIndex)
            elif flush:
                self._fd[fileIndex][1].flush(offsetInFile, lengthToWrite)

            fileIndex += 1
            offsetInFile = 0
        
        # report piece downloaded event
        if offset + len(data) == self.torrentContext.metaInfo.pieceLength:
            self._pieceDownloaded(pieceIndex)

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

    def _fileDownloaded(self, fileIndex):
        self._fd[fileIndex][1].flush()
        self.torrentContext.files[fileIndex].downloaded = True
        self.delegation.fileDownloaded(fileIndex)

    def start(self):
        # The library directory
        if not self.library.exists():
            self.library.mkdir()
        if not self.library.is_dir():
            raise OSError('Download is not a directory.')
        logger.debug('Library initialized')

        # Root directory of this storage
        if self.ctx.isSingleFile():
            logger.debug('It is a single-file torrent.')
            self.root = self.library
        else:
            logger.debug('It is a multiple-files torrent.')
            self.root = Path(self.library, self.ctx.getName())
            if not self.root.exists():
                self.root.mkdir()
                logger.info('Directory created.')
            elif self.root.is_file:
                raise OSError('Root directory exists but it is a file.')

        # Open all files
        for fileInfo in self.ctx.files:
            file = Path(self.root, *fileInfo.path, fileInfo.name)
            # Create the file if not exists
            if not file.exists():
                with open(file, 'wb') as fd:
                    if fileInfo.length > 0:
                        fd.seek(fileInfo.length - 1)
                        fd.write(b'\0')
            fd = open(file, 'r+b')
            self._fd.append((fd, mmap(fd.fileno(), 0)))
            logger.info('File %s has been created.', fileInfo.name)

    def shutdown(self):
        for fd in self._fd:
            fd[1].close()
            fd[0].close()
