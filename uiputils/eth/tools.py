from ctypes import CDLL
from uiputils.gotypes import GoString, GoInt32, GoStringSlice, GolevelDBptr
from eth_hash.auto import keccak
from uiputils.cast import fillbytes32, catbytes32, bytestoint, fillint32, transbytes32, catint32, transint
from uiputils import INCLUDE_PATH
from hexbytes import HexBytes
# from sys import path as loadpathlist
from os import path as parsepath
# if pathofinclude not in loadpathlist:
#     loadpathlist.append(pathofinclude)
# print("\n".join(loadpathlist))


ENC = "utf-8"
MOD256 = (1 << 256) - 1

funcs = CDLL(INCLUDE_PATH + "/verifyproof.dll")

funcs.openDB.restype = GolevelDBptr
funcs.openDB.argtype = GoString.Type

funcs.closeDB.argtype = GolevelDBptr

funcs.VerifyProof.restype = GoInt32
funcs.VerifyProof.argtypes = (GolevelDBptr, GoString.Type, GoString.Type, GoString.Type, GoStringSlice.Type, GoInt32)


class Prover:
    def __init__(self, path):
        if path == "":
            self.testmode = True
        else:
            self.testmode = False
            self.ethdb = funcs.openDB(bytes(path.encode(ENC)))

    def close(self):
        if self.testmode:
            print("you are in testmode")
            return None
        funcs.closeDB(self.ethdb)

    def verifyhaspath(self, key, val, storagehash, storagepath):
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

        print("TODO of verify")
        # funcs.VerifyProof(self.ethdb, hashptr, keyptr, valptr, path, len(storagepath))


def sliceloc32(bytesslot, index, element_size):
    return catint32(bytestoint(keccak(bytesslot)) + (index * element_size))


def sliceloc(bytesslot, index, element_size):
    return catint32(bytestoint(keccak(fillbytes32(bytesslot))) + (index * element_size))


def slicelocbyint(intslot, index, element_size):
    return catint32(bytestoint(keccak(fillint32(intslot))) + (index * element_size))


def slicelocation(slot, index, element_size):
    return sliceloc32(transbytes32(slot), transint(index), element_size)


def maploc32(bytesslot, byteskey):
    return keccak(bytesslot + byteskey)


def maploc(bytesslot, byteskey):
    return keccak(catbytes32(bytesslot) + catbytes32(byteskey))


def maplocation(slot, key):
    return keccak(transbytes32(key) + transbytes32(slot))


# the var of bytestoint(keccak(fillint32(SLOT_WAITING_QUEUE)))
POS_WAITING_QUEUE = 18569430475105882587588266137607568536673111973893317399460219858819262702947
POS_MERKLEPROOFTREE = b'\x00'*31 + b'\x06'
POS_ACTIONTREE = b'\x00'*31 + b'\x08'


class LocationTransLator(object):
    # calculate varible's location of NSB

    @staticmethod
    def queueloc(index):
        return catint32(POS_WAITING_QUEUE + index)

    @staticmethod
    def merkleloc(keccakhash):
        return keccak(keccakhash + POS_MERKLEPROOFTREE)

    @staticmethod
    def actionloc(keccakhash):
        return keccak(keccakhash + POS_ACTIONTREE)

    slicesto = slicelocation

    mapsto = maplocation


if __name__ == '__main__':
    print(HexBytes(sliceloc(b'\x01', 1, 8)).hex())
    print(HexBytes(slicelocation(b'\x01', 1, 8)).hex())
    print(HexBytes(slicelocation(1, 1, 16)).hex())
    print(HexBytes(slicelocation("1", 1, 8)).hex())
    print(HexBytes(slicelocation("0x1", 1, 8)).hex())
    print(HexBytes(maploc(b'\x00', b'\x00')).hex())
