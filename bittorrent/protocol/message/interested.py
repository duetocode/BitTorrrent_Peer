from .main import EmptyMessage

class Interested(EmptyMessage):

    def __init__(self):
        self.id = 2

    @classmethod
    def parse(clazz, rawData):
        return Interested()