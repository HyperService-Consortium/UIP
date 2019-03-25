
'some cast methods'

# python modules
import json
from functools import partial
import rlp

# ethereum modules
from hexbytes import HexBytes

# uip modules
from uiputils.uiperror import DecodeFail

# constant
MOD512 = (1 << 512) - 1
MOD256 = (1 << 256) - 1
MOD8 = (1 << 8) - 1


def uintxstring(num, length):
    # return x-bit string of num
    nums = str(num)
    return "0" * (length - len(nums)) + nums


def uint32string(num):
    # return 32-bit string of num
    nums = str(num)
    return "0" * (32 - len(nums)) + nums


def uint64string(num):
    # return 64-bit string of num
    nums = str(num)
    return "0" * (64 - len(nums)) + nums


def uint128string(num):
    # return 128-bit string of num
    nums = str(num)
    return "0" * (128 - len(nums)) + nums


def uint256string(num):
    # return 256-bit string of num
    nums = str(num)
    return "0" * (256 - len(nums)) + nums


def uintxhexstring(num, length):
    # return x-bit string of num
    nums = str(hex(num))
    return "0" * (length - len(nums)) + nums


def uint32hexstring(num):
    # return 32-bit string of num
    nums = str(hex(num))[2:]
    return "0" * (32 - len(nums)) + nums


def uint64hexstring(num):
    # return 64-bit string of num
    nums = str(hex(num))[2:]
    return "0" * (64 - len(nums)) + nums


def uint128hexstring(num):
    # return 128-bit string of num
    nums = str(hex(num))[2:]
    return "0" * (128 - len(nums)) + nums


def uint256hexstring(num):
    # return 256-bit string of num
    nums = str(hex(num))[2:]
    return "0" * (256 - len(nums)) + nums


def fillbytes(bytes_slice, length):
    return b'\x00' * (length - len(bytes_slice)) + bytes_slice


def fillbytes32(bytes_slice):
    return b'\x00' * (32 - len(bytes_slice)) + bytes_slice


def fillbytes64(bytes_slice):
    return b'\x00' * (64 - len(bytes_slice)) + bytes_slice


def fillstring(chars_slice, length):
    chars_slice = HexBytes(chars_slice)
    return b'\x00' * (length - len(chars_slice)) + chars_slice


def fillstring32(chars_slice):
    chars_slice = HexBytes(chars_slice)
    return b'\x00' * (32 - len(chars_slice)) + chars_slice


def fillstring64(chars_slice):
    chars_slice = HexBytes(chars_slice)
    return b'\x00' * (64 - len(chars_slice)) + chars_slice


def catbytes(bytes_slice, length):
    if len(bytes_slice) > length:
        return bytes_slice[-length:]
    else:
        return b'\x00' * (length - len(bytes_slice)) + bytes_slice


def catbytes32(bytes_slice):
    if len(bytes_slice) > 32:
        return bytes_slice[-32:]
    else:
        return b'\x00' * (32 - len(bytes_slice)) + bytes_slice


def catbytes64(bytes_slice):
    if len(bytes_slice) > 64:
        return bytes_slice[-64:]
    else:
        return b'\x00' * (64 - len(bytes_slice)) + bytes_slice


def catstring(chars_slice, length):
    chars_slice = HexBytes(chars_slice)
    if len(chars_slice) > length:
        return chars_slice[-length:]
    else:
        return b'\x00' * (length - len(chars_slice)) + chars_slice


def catstring32(chars_slice):
    chars_slice = HexBytes(chars_slice)
    if len(chars_slice) > 32:
        return chars_slice[-32:]
    else:
        return b'\x00' * (32 - len(chars_slice)) + chars_slice


def catstring64(chars_slice):
    chars_slice = HexBytes(chars_slice)
    if len(chars_slice) > 64:
        return chars_slice[-64:]
    else:
        return b'\x00' * (64 - len(chars_slice)) + chars_slice


def fillint(integer, length):
    return fillbytes(HexBytes(integer), length)


# follow function causes OverFlowError
# fillint32 = partial(int.to_bytes, length=32, byteorder="big")


def fillint32(integer):
    return fillbytes(HexBytes(integer), 32)


def fillint64(integer):
    return fillbytes(HexBytes(integer), 64)


def catint(integer, length):
    return (integer & ((1 << (length << 3)) - 1)).to_bytes(length=length, byteorder="big")


def catint32(integer):
    return (integer & MOD256).to_bytes(length=32, byteorder="big")


def catint64(integer):
    return (integer & MOD512).to_bytes(length=64, byteorder="big")


def transbytes(anytype, length):
    if isinstance(anytype, int):
        return catstring(hex(anytype), length)
    elif isinstance(anytype, str):
        return catstring(anytype, length)
    elif isinstance(anytype, bytes):
        return catbytes(anytype, length)
    else:
        raise TypeError("Unexpected Type when translating element to bytes32", anytype.__class__)


def transbytes32(anytype):
    if isinstance(anytype, int):
        return catstring32(hex(anytype))
    elif isinstance(anytype, str):
        return catstring32(anytype)
    elif isinstance(anytype, bytes):
        return catbytes32(anytype)
    else:
        raise TypeError("Unexpected Type when translating element to bytes32", anytype.__class__)


def transbytes64(anytype):
    if isinstance(anytype, int):
        return catstring64(hex(anytype))
    elif isinstance(anytype, str):
        return catstring64(anytype)
    elif isinstance(anytype, bytes):
        return catbytes64(anytype)
    else:
        raise TypeError("Unexpected Type when translating element to bytes64", anytype.__class__)


bytestoint = partial(int.from_bytes, byteorder="big")


def showbytes(hex_bytes):
    return [hex_bytes[x] for x in range(len(hex_bytes))]


def transint(anytype):
    if isinstance(anytype, int):
        return anytype
    elif isinstance(anytype, bytes):
        return bytestoint(anytype)
    elif isinstance(anytype, str):
        return int(anytype, 16)
    else:
        raise TypeError("Unexpected Type when translating element to int")


def dict_serializable(dct: dict):
    rlplist = ['as_dict']
    for k, v in dct.items():
        tlp: list
        if isinstance(v, str) or isinstance(v, bytes):
            tlp = [k, v]
        elif isinstance(v, list):
            for idx, ele in enumerate(v):
                if isinstance(ele, dict):
                    v[idx] = dict_serializable(ele)
            tlp = [k, ['as_list'] + v]
        elif isinstance(v, int):
            tlp = [k, hex(v)]
        elif isinstance(v, dict):
            tlp = [k, dict_serializable(v)]
        elif v is None:
            tlp = [k]
        rlplist.append(tlp)
    return rlplist


def dict_serialize(dct: dict):
    return rlp.encode(dict_serializable(dct))


def dict_unserialize_decode(rlped_elem):
    if isinstance(rlped_elem, list):
        if len(rlped_elem) == 0:
            return rlped_elem
        if rlped_elem[0] == b'as_dict':
            ret = {}
            for ele in rlped_elem[1:]:
                if not isinstance(ele, list) or len(ele) > 2 or len(ele) == 0:
                    raise DecodeFail("element is not a unserializable list-pair")
                if len(ele) == 2:
                    ret[ele[0].decode('utf-8')] = dict_unserialize_decode(ele[1])
                else:
                    ret[ele[0].decode('utf-8')] = None
            return ret
        elif rlped_elem[0] == b'as_list':
            return [dict_unserialize_decode(ele) for ele in rlped_elem[1:]]
    else:
        return rlped_elem


def dict_unserialize(rlped_elem):
    return dict_unserialize_decode(rlp.decode(rlped_elem))


class DictRlpize(object):
    # rlp methods of dict
    serializable = staticmethod(dict_serializable)

    serialize = staticmethod(dict_serialize)

    unserialize = staticmethod(dict_unserialize)


# TODO: JsonRlpize
class JsonRlpize(object):
    # rlp methods of dict
    serializable = staticmethod(dict_serializable)

    serialize = staticmethod(dict_serialize)

    unserialize = staticmethod(dict_unserialize)


class Cast(object):
    # use arbi.func(obj, len)
    tostring = staticmethod(uintxstring)

    tohexstring = staticmethod(uintxhexstring)

    toint = staticmethod(transint)

    tointfrombytes = staticmethod(bytestoint)

    tobytes = staticmethod(transbytes)

    tobytesfrombytes = staticmethod(catbytes)

    tobytesfromstring = staticmethod(catstring)

    tobytesfromint = staticmethod(catint)


class Cast32(object):
    # use Cast32.func(obj)
    tostring = staticmethod(uint32string)

    tohexstring = staticmethod(uint32hexstring)

    toint = staticmethod(transint)

    tointfrombytes = staticmethod(bytestoint)

    tobytes = staticmethod(transbytes32)

    tobytesfrombytes = staticmethod(catbytes32)

    tobytesfromstring = staticmethod(catstring32)

    tobytesfromint = staticmethod(catint32)


class Cast64(object):
    # use Cast64.func(obj)
    tostring = staticmethod(uint64string)

    tohexstring = staticmethod(uint64hexstring)

    toint = staticmethod(transint)

    tointfrombytes = staticmethod(bytestoint)

    tobytes = staticmethod(transbytes64)

    tobytesfrombytes = staticmethod(catbytes64)

    tobytesfromstring = staticmethod(catstring64)

    tobytesfromint = staticmethod(catint64)


class Mult(object):
    # use Must.cast(len, objs)
    @staticmethod
    def tostring(length, *args):
        return [uintxstring(obj, length) for obj in args]

    @staticmethod
    def tohexstring(length, *args):
        return [uintxhexstring(obj, length) for obj in args]

    @staticmethod
    def toint(*args):
        return [transint(obj) for obj in args]

    @staticmethod
    def tointfrombytes(*args):
        return [bytestoint(obj) for obj in args]

    @staticmethod
    def tobytes(length, *args):
        return [transbytes(obj, length) for obj in args]

    @staticmethod
    def tobytesfrombytes(length, *args):
        return [catbytes(obj, length) for obj in args]

    @staticmethod
    def tobytesfromstring(length, *args):
        return [catstring(obj, length) for obj in args]

    @staticmethod
    def tobytesfromint(length, *args):
        return [catint(obj, length) for obj in args]


class Mult32(object):
    # use Mult32.cast(objs)
    @staticmethod
    def tostring(*args):
        return [uint32string(obj) for obj in args]

    @staticmethod
    def tohexstring(*args):
        return [uint32hexstring(obj) for obj in args]

    @staticmethod
    def toint(*args):
        return [transint(obj) for obj in args]

    @staticmethod
    def tointfrombytes(*args):
        return [bytestoint(obj) for obj in args]

    @staticmethod
    def tobytes(*args):
        return [transbytes32(obj) for obj in args]

    @staticmethod
    def tobytesfrombytes(*args):
        return [catbytes32(obj) for obj in args]

    @staticmethod
    def tobytesfromstring(*args):
        return [catstring32(obj) for obj in args]

    @staticmethod
    def tobytesfromint(*args):
        return [catint32(obj) for obj in args]


class Mult64(object):
    # use Mult64.cast(objs)
    @staticmethod
    def tostring(*args):
        return [uint64string(obj) for obj in args]

    @staticmethod
    def tohexstring(*args):
        return [uint64hexstring(obj) for obj in args]

    @staticmethod
    def toint(*args):
        return [transint(obj) for obj in args]

    @staticmethod
    def tointfrombytes(*args):
        return [bytestoint(obj) for obj in args]

    @staticmethod
    def tobytes(*args):
        return [transbytes64(obj) for obj in args]

    @staticmethod
    def tobytesfrombytes(*args):
        return [catbytes64(obj) for obj in args]

    @staticmethod
    def tobytesfromstring(*args):
        return [catstring64(obj) for obj in args]

    @staticmethod
    def tobytesfromint(*args):
        return [catint64(obj) for obj in args]


def formated_json(inputdict):
    return json.dumps(inputdict, sort_keys=True, indent=4, separators=(', ', ': '))


if __name__ == '__main__':
    dit = {
        'from': "12345678",
        'to': "87654321",
        "data": {
            "src": "abcdefg",
            "domain": "Ethereum",
            "json": [{'from': 'a'}, {'to': 'a'}],
            "data": b"123",
            "data2": 255,
            "data3": True,
            "data4": False
        },
        "json": None
    }
    print(DictRlpize.serializable(dit))
    rlped_dit = DictRlpize.serialize(dit)
    print(rlped_dit)
    print(DictRlpize.unserialize(rlped_dit))
    # print(uintxstring(15, 8))
    # print(uint32string(15))
    # print(uint64string(15))
    # print(uint128string(15))
    # print(uintxhexstring(15, 8))
    # print(uint32hexstring(15))
    # print(uint64hexstring(15))
    # print(uint128hexstring(15))
    # print(uint64hexstring(int('0x0', 16)))
    print(fillint(299999, 5))
    print(catint32(bytestoint(b'\xff' * 33)))
    print(fillint32(bytestoint(b'\xff' * 31)))
    print(fillbytes32(HexBytes('123')))
    print(fillstring32('123'))
    print(catbytes(fillbytes32(b'\x01\x22'), 4))
    print(fillbytes(b'\x01\x22', 8))
