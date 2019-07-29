
class Endpoint:

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __hash__(self):
        return hash((self.host, self.port))

    def __eq__(self, value):
        if value is None:
            return False

        if not isinstance(value, Endpoint):
            return False

        return self.host == value.host and self.port == value.port

    def __str__(self):
        return f'{self.host}:{self.port}'        
        

