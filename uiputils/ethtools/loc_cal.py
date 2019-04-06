
# ethereum modules
from eth_hash.auto import keccak

# uip modules
from uiputils.uiptools.cast import (
    fillbytes32,
    catbytes32,
    bytestoint,
    fillint32,
    transbytes32,
    catint32,
    transint
)

# constant
#   the var of bytestoint(keccak(fillint32(SLOT_WAITING_QUEUE)))
POS_WAITING_QUEUE = 18569430475105882587588266137607568536673111973893317399460219858819262702947
#   Merkleprooftree position
POS_MERKLEPROOFTREE = b'\x00' * 31 + b'\x06'
#   Actiontree position
POS_ACTIONTREE = b'\x00' * 31 + b'\x08'


def sliceloc32(slot: bytes, index: int, element_size: int) -> bytes:
    return catint32(bytestoint(keccak(slot)) + (index * element_size))


def sliceloc(slot: bytes, index: int, element_size: int) -> bytes:
    return catint32(bytestoint(keccak(fillbytes32(slot))) + (index * element_size))


def slicelocbyint(slot: int, index: int, element_size: int) -> bytes:
    return catint32(bytestoint(keccak(fillint32(slot))) + (index * element_size))


def slicelocation(slot, index, element_size) -> bytes:
    return sliceloc32(transbytes32(slot), transint(index), element_size)


def maploc32(slot: bytes, key: bytes) -> bytes:
    return keccak(slot + key)


def maploc(slot: bytes, key: bytes) -> bytes:
    return keccak(catbytes32(slot) + catbytes32(key))


def maplocation(slot, key) -> bytes:
    return keccak(transbytes32(key) + transbytes32(slot))


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

    slicesto = staticmethod(slicelocation)

    mapsto = staticmethod(maplocation)


class SliceLoc(object):
    def __init__(self):
        pass

    withslot32 = staticmethod(sliceloc32)

    withslot = staticmethod(sliceloc)

    withslotint = staticmethod(slicelocbyint)

    cast = staticmethod(slicelocation)


class MapLoc(object):
    def __init__(self):
        pass

    withslot32 = staticmethod(maploc32)

    withslot = staticmethod(maploc)

    cast = staticmethod(maplocation)
