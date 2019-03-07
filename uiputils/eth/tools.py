
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
        funcs.VerifyProof(self.ethdb,
                          storagehash,
                          key, val,
                          GoStringSlice.fromstrlist(storagepath, ENC),
                          len(storagepath))
