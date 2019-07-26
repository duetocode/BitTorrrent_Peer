from .main import EmptyMessage

class Choke(EmptyMessage):

    def __init__(self):
        self.id = 0
        
    @classmethod
    def parse(clazz, rawData):
        return Choke()