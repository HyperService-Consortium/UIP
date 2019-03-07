
import ctypes

GoInt8 = ctypes.c_int8
GoInt16 = ctypes.c_int16
GoInt32 = ctypes.c_int32
GoInt64 = ctypes.c_int64

GoUint8 = ctypes.c_uint8
GoUint16 = ctypes.c_uint16
GoUint32 = ctypes.c_uint32
GoUint64 = ctypes.c_uint64

GoInt = GoUint64
GoUInt = GoUint64

GolevelDBptr = ctypes.c_int


class GoBytes(object):
    # GoBytes in C
    Type = ctypes.c_char_p

    @staticmethod
    def frombytes(bytesarr):
        return ctypes.c_char_p(bytesarr)


class GoString(object):
    # GoString in C

    Type = ctypes.POINTER(ctypes.c_char)

    @staticmethod
    def fromstr(pystr, enc):
        return ctypes.c_char_p(bytes(pystr.encode(enc)))


class GoStringSlice(object):
    # GoStringSlice in C

    Type = ctypes.POINTER(GoString.Type)

    @staticmethod
    def fromstrlist(strlist, enc):
        strs = [ctypes.c_char_p(bytes(path.encode(enc))) for path in strlist]
        charparray = ctypes.c_char_p * len(strlist)
        charlist = charparray(*strs)
        return ctypes.cast(charlist, GoStringSlice.Type)
