
# python modules
from ctypes import CDLL

# uip modules
from uiputils.gotypes import (
    GoString,
    GoInt32,
    GoStringSlice,
    GolevelDBptr
)

# config
from uiputils.config import INCLUDE_PATH
ENC = "utf-8"

# Prover functions setting
funcs = CDLL(INCLUDE_PATH + "/verifyproof.dll")

funcs.OpenDB.restype = GolevelDBptr
funcs.OpenDB.argtype = GoString.Type

funcs.CloseDB.argtype = GolevelDBptr

funcs.VerifyProof.restype = GoInt32
funcs.VerifyProof.argtypes = (GolevelDBptr, GoString.Type, GoString.Type, GoString.Type, GoStringSlice.Type, GoInt32)

funcs.VerifyProofWithoutPath.restype = GoInt32
funcs.VerifyProofWithoutPath.argtypes = (GolevelDBptr, GoString.Type, GoString.Type, GoString.Type)


class Prover:
    def __init__(self, path):
        if path == "":
            self.testmode = True
        else:
            self.testmode = False
            self.ethdb = funcs.OpenDB(bytes(path.encode(ENC)))

    def close(self):
        if self.testmode:
            print("you are in testmode")
            return None
        funcs.CloseDB(self.ethdb)

    def verify(self, merkleproof):
        if self.testmode:
            print("you are in testmode")
            return None
        keyptr = GoString.trans(merkleproof.key, ENC)
        if keyptr == 'error':
            raise TypeError("key-type needs str or bytes, but get", merkleproof.key.__class__)

        valptr = GoString.trans(merkleproof.value, ENC)
        if valptr == 'error':
            raise TypeError("val-type needs str or bytes, but get", merkleproof.value.__class__)

        hashptr = GoString.trans(merkleproof.storagehash, ENC)
        if hashptr == 'error':
            raise TypeError("storageHash-type needs str or bytes, but get", merkleproof.storagehash.__class__)

        funcs.VerifyProofWithoutPath(self.ethdb, hashptr, keyptr, valptr)

    def verify_with_path(self, key, val, storagehash, storagepath):
        if self.testmode:
            print("you are in testmode")
            return None
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
