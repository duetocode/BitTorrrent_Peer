from .choke import Choke
from .unchoke import Unchoke
from .interested import Interested
from .not_interested import NotInterested
from .have import Have
from .bitfield import Bitfield

MESSAGE_CLASSES = [Choke, Unchoke, Interested, NotInterested, Have, Bitfield]

def parse(rawData):
    messageId = rawData[0]

    if messageId > 0 and messageId < len(MESSAGE_CLASSES):
        return MESSAGE_CLASSES[messageId].parse(rawData)
    else:
        return None
    