class ByteStringBuffer:

    def __init__(self, buf):
        self._buf = buf
        self._pointer = 0

    def peek(self):
        if self.isEmpty():
            raise IndexError('Peek at an empty buffer.')
        return self._buf[self._pointer]
    
    def pop(self, length=1, decodeSingle=True):
        newPosition = self._pointer + length
        if newPosition > len(self._buf):
            raise IndexError('Not enough data in buffer.')
        
        data = self._buf[self._pointer:newPosition]
        self._pointer = newPosition
        if decodeSingle and length == 1:
            return data[0]
        else:
            return data

    def isEmpty(self):
        return self._buf is None or len(self._buf) == 0
    
    def popTo(self, character):
        index = self._pointer
        while index < len(self._buf) and character != self._buf[index]:
            index += 1
        
        if index < len(self._buf):
            return self.pop(index - self._pointer + 1, decodeSingle=False)[:-1]
        else:
            return None
    
    def __len__(self):
        return len(self._buf) - self._pointer

class IllegalBencodingData(Exception):
    pass        

def decode(buf):

    byte = buf.peek()

    if byte == ord('i'):
        return decodeInteger(buf)
    elif byte == ord('l'):
        return decodeList(buf)
    elif byte == ord('d'):
        return decodeDict(buf)
    elif isNumber(byte):
        return decodeByteString(buf)
    else:
        raise IllegalBencodingData()


def decodeInteger(buf:ByteStringBuffer):
    assert buf.pop() == ord('i')
    return int(buf.popTo(ord('e')))
    
def decodeByteString(buf:ByteStringBuffer):
    # Read length
    length = int(buf.popTo(ord(':')))
    
    # Check
    if length > len(buf):
        raise IllegalBencodingData()
    
    return buf.pop(length=length, decodeSingle=False)

def isNumber(c):
    return type(c) == int and c >= 48 and c <= 57

def decodeList(buf:ByteStringBuffer):
    assert buf.pop() == ord('l')
    result = []
    while buf.peek() != ord('e'):
        result.append(decode(buf))
    
    buf.pop()

    return result

def decodeDict(buf:ByteStringBuffer):
    assert buf.pop() == ord('d')

    result = Bulk()
    while buf.peek() != ord('e'):
        key = decode(buf).decode('utf-8')
        value = decode(buf)
        result[key] = value

    buf.pop()

    return result


class Bulk(dict):

    def __getattribute__(self, name):
        if name in self:
            return self[name]