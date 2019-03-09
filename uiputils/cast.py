
'some cast methods'

from hexbytes import HexBytes
from functools import partial

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
    return (integer & MOD256).to_bytes(length=length, byteorder="big")


def catint32(integer):
    return (integer & MOD256).to_bytes(length=32, byteorder="big")


def catint64(integer):
    return (integer & MOD256).to_bytes(length=64, byteorder="big")


def transbytes32(anytype):
    if isinstance(anytype, int):
        return catstring32(hex(anytype))
    elif isinstance(anytype, str):
        return catstring32(anytype)
    elif isinstance(anytype, bytes):
        return catbytes32(anytype)
    else:
        raise TypeError("Unexpected Type when translating element to bytes32", anytype.__class__)


def transint(anytype):
    if isinstance(anytype, int):
        return anytype
    elif isinstance(anytype, bytes):
        return bytestoint(anytype)
    elif isinstance(anytype, str):
        return int(anytype, 16)
    else:
        raise TypeError("Unexpected Type when translating element to int")


bytestoint = partial(int.from_bytes, byteorder="big")


if __name__ == '__main__':
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
