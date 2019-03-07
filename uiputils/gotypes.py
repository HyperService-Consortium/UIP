
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

GoBytes = ctypes.c_char_p
GoString = ctypes.POINTER(ctypes.c_char)
GoStringSlice = ctypes.POINTER(GoString)