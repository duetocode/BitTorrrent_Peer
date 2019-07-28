
class PieceState:
    Unknown = -1
    NotHave = 0
    Have = 1
    Downloading = 2

class PieceInfo:

    def __init__(self, index=0, state=PieceState.Unknown):
        self.index = index
        self.state = state
        self.hash = None