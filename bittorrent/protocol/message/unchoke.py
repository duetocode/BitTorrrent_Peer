from .main import EmptyMessage

class Unchoke(EmptyMessage):

    def __init__(self):
        self.id = 1

    @classmethod
    def parse(clazz, rawData):
        return Unchoke()