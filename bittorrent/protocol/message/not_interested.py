from .main import EmptyMessage

class NotInterested(EmptyMessage):

    def __init__(self):
        self.id = 3
        
    @classmethod
    def parse(clazz, rawData):
        return NotInterested()