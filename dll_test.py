from ctypes import *

PROVER_PATH = "./scripts/verifyproof.dll"
EDB_PATH = "D:/Go Ethereum/data/geth/chaindata"
ENC = "utf-8"

StorageHash = b"0x11e91152ab237ceff29728c03999ef2debadd7db0fc45b280657c6f7cc4c1ffa"
StoragePath = ["f8918080a06d032ff808e3a2b585df339916901d7b7d04c5bd18a088607093d3178172b7ee8080808080a0071b011fdbd4ad7d1e6f9762be4d1a88dffde614a6bd399bf3b5bad8f41249b5808080a01b56cc0a5b9b1ce34e9a14e896ea000c830bd64387573d238cbe3fa24ddfa2c3a0f5c2efa606e3a5be341f22bf1d5c8f4bce679719870c097a24abb38aec0a4855808080", "f8518080808080a06f643b8fd2176a403e2ccfae43808c4543289e1082078e91d821d1c7886d6f51808080a03822ab26403807d175522401e184b20b5aa8c7fcd802f4793970a70e810f4ce980808080808080", "e2a0200decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e56333"]

key = b"0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563"
val = b"0x33"

GoInt8 = c_int8
GoInt16 = c_int16
GoInt32 = c_int32
GoInt64 = c_int64

GoUint8 = c_uint8
GoUint16 = c_uint16
GoUint32 = c_uint32
GoUint64 = c_uint64

GoInt = GoUint64
GoUInt = GoUint64

GoBytes = c_char_p
GoString = POINTER(c_char)
GoStringSlice = POINTER(GoString)

dbptr = c_void_p

funcs = CDLL(PROVER_PATH)

funcs.openDB.restype = dbptr
funcs.openDB.argtype = GoString

funcs.closeDB.argtype = dbptr

funcs.VerifyProof.restype = GoInt32
funcs.VerifyProof.argtypes = (dbptr, GoString, GoString, GoString, GoStringSlice, GoInt32)


class Prover:
    def __init__(self, path):
        self.ethdb = funcs.openDB(bytes(path.encode(ENC)))

    def close(self):
        funcs.closeDB(self.ethdb)

    def verify(self, StorageHash, key, val, StoragePath):
        strs = [c_char_p(bytes(path.encode(ENC))) for path in StoragePath]
        lenx = len(StoragePath)
        charparray = c_char_p * lenx
        charlist = charparray(*strs)
        funcs.VerifyProof(self.ethdb, StorageHash, key, val, cast(charlist, POINTER(POINTER(c_char))), lenx)


if __name__ == '__main__':

    prover = Prover(EDB_PATH)

    prover.verify(StorageHash, key, val, StoragePath)

    prover.close()

