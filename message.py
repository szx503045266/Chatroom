import socket
import enum
from struct import pack, unpack

class MessageType(enum.IntEnum):
    connect_request = 1
    connect_confirm = 2
    connect_refuse = 3

    login_info = 4
    login_confirm = 5
    login_refuse = 6

    chat_message = 10

    name_request = 20
    name_info = 21


class ByteArrayReader:
    def __init__(self, byte_array):
        self.byte_array = byte_array
        self.pointer = 0

    def read(self, length):
        buffer = self.byte_array[self.pointer: self.pointer + length]
        self.pointer += length
        return buffer

    def read_to_end(self):
        buffer = self.byte_array[self.pointer: len(self.byte_array)]
        self.pointer = len(self.byte_array)
        return buffer

    def empty(self):
        return len(self.byte_array) == self.pointer

Body_TYPE = {
    1: 'str',
    2: 'int'
}

Body_TYPE_r = {
    'str': 1,
    'int': 2
}

###### Message packing and unpacking ######

def serialize_str(message):
    body = message.encode('utf-8')
    return bytes([Body_TYPE_r['str']]) + pack('!L', len(body)) + body

def serialize_int(message):
    body = pack('!L', message)
    return bytes([Body_TYPE_r['int']]) + pack('!L', len(body)) +body

def serialize(message):
    if type(message) == str:
        return serialize_str(message)
    elif type(message) == int:
        return serialize_int(message)

def packing_message(sender, message_type, message):
    packed_message = pack('!L', sender) + bytes([message_type.value]) + serialize(message)
    return packed_message

def deserialize_str(byte_reader):
    l_buffer = byte_reader.read(4)
    l = unpack('!L', l_buffer)[0]
    body_buffer = byte_reader.read_to_end()
    body = body_buffer.decode('utf-8')
    return l, body

def deserialize_int(byte_reader):
    l_buffer = byte_reader.read(4)
    l = unpack('!L', l_buffer)[0]
    body_buffer = byte_reader.read(4)
    body = unpack('!L', body_buffer)[0]
    return l, body

def deserialize(byte_reader):
    body_type = byte_reader.read(1)[0]
    if Body_TYPE[body_type] == 'str':
        return deserialize_str(byte_reader)
    elif Body_TYPE[body_type] == 'int':
        return deserialize_int(byte_reader)

def unpacking_message(packed_message):
    byte_reader = ByteArrayReader(packed_message)

    sender_buffer = byte_reader.read(4)
    sender = unpack('!L', sender_buffer)[0]
    message_type_num = byte_reader.read(1)[0]
    message_type = MessageType(message_type_num)
    _, message = deserialize(byte_reader)

    return sender, message_type, message