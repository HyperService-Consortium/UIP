
from ctypes import CDLL
from uiputils.gotypes import GoString, GoInt32, GoStringSlice, GolevelDBptr

PROVER_PATH = "./uiputils/include/verifyproof.dll"
ENC = "utf-8"

funcs = CDLL(PROVER_PATH)

funcs.openDB.restype = GolevelDBptr
funcs.openDB.argtype = GoString.Type

funcs.closeDB.argtype = GolevelDBptr

funcs.VerifyProof.restype = GoInt32
funcs.VerifyProof.argtypes = (GolevelDBptr, GoString.Type, GoString.Type, GoString.Type, GoStringSlice.Type, GoInt32)


class Prover:
    def __init__(self, path):
        self.ethdb = funcs.openDB(bytes(path.encode(ENC)))

    def close(self):
        funcs.closeDB(self.ethdb)

    def verify(self, key, val, storagehash, storagepath):
        keyptr = GoString.trans(key, ENC)
        if keyptr == 'error':
            raise TypeError("key-type needs str or bytes, but get", key.__class__)

        valptr = GoString.trans(val, ENC)
        if valptr == 'error':
            raise TypeError("val-type needs str or bytes, but get", val.__class__)

        hashptr = GoString.trans(storagehash, ENC)
        if hashptr == 'error':
            raise TypeError("storageHash-type needs str or bytes, but get", storagehash.__class__)

        path = GoStringSlice.fromstrlist(storagepath, ENC)

        funcs.VerifyProof(self.ethdb, hashptr, keyptr, valptr, path, len(storagepath))
