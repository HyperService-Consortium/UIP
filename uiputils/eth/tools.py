
# python modules
import re
from ctypes import CDLL

# uip modules
from uiputils.gotypes import (
    GoString,
    GoInt32,
    GoStringSlice,
    GolevelDBptr
)
from uiputils.cast import (
    fillbytes32,
    catbytes32,
    bytestoint,
    fillint32,
    transbytes32,
    catint32,
    transint
)
from uiputils.uiperror import Mismatch, SolidityTypeError

# ethereum modules
from eth_hash.auto import keccak
from hexbytes import HexBytes
from eth_keys import KeyAPI
from web3 import Web3

# self-package modules

# config
from uiputils.config import INCLUDE_PATH, ETHSIGN_HEADER

# constant
ENC = "utf-8"
INTM = [(1 << (bit_size << 3)) for bit_size in range(33)]

# Prover functions setting
funcs = CDLL(INCLUDE_PATH + "/verifyproof.dll")

funcs.OpenDB.restype = GolevelDBptr
funcs.OpenDB.argtype = GoString.Type

funcs.CloseDB.argtype = GolevelDBptr

funcs.VerifyProof.restype = GoInt32
funcs.VerifyProof.argtypes = (GolevelDBptr, GoString.Type, GoString.Type, GoString.Type, GoStringSlice.Type, GoInt32)

funcs.VerifyProofWithoutPath.restype = GoInt32
funcs.VerifyProofWithoutPath.argtypes = (GolevelDBptr, GoString.Type, GoString.Type, GoString.Type)

# constant
MOD256 = (1 << 256) - 1
MOD6 = (1 << 6) - 1
BYTE32_LENGTH = 64

# the var of bytestoint(keccak(fillint32(SLOT_WAITING_QUEUE)))
POS_WAITING_QUEUE = 18569430475105882587588266137607568536673111973893317399460219858819262702947

# Merkleprooftree position
POS_MERKLEPROOFTREE = b'\x00' * 31 + b'\x06'

# Actiontree position
POS_ACTIONTREE = b'\x00' * 31 + b'\x08'

hex_match = re.compile(r'\b[0-9a-fA-F]+\b')
hex_match_withprefix = re.compile(r'\b0x[0-9a-fA-F]+\b')


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

        funcs.VerifyProofWithoutPath(self.ethdb, hashptr, keyptr, valptr)


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


class AbiEncoder:
    def __init__(self):
        pass

    @staticmethod
    def encode(para_type, para):
        if para_type == 'address':
            return AbiEncoder.encode('uint160', para)
        elif para_type == 'string':
            return AbiEncoder.encode('bytes', para.encode('utf-8'))
        elif para_type == 'byte':
            return AbiEncoder.encode('bytes1', para)
        elif para_type == 'bool':
            return AbiEncoder.encode('uint8', para)
        elif para_type[-1] == ']':  # Array
            if not hasattr(para, '__iter__'):
                raise TypeError("not iteraable parameter " + str(para) + " for Array type " + para_type)
            array_type, array_size = para_type[:-1].split('[')
            if array_size != "":
                if int(array_size) < len(para):  # != ?
                    raise Mismatch('parameters mismatch with parameters_type')
                return ''.join((AbiEncoder.encode(array_type, ele) for ele in para))
            else:  # bug __iter__ -> __len__ ?
                return AbiEncoder.encode('uint256', len(para)) + \
                       ''.join((AbiEncoder.encode(array_type, ele) for ele in para))
        elif para_type[0:3] == 'int':
            numstr, negative_flag = para, '0'
            numsize = para_type[3:]
            if numsize == "":
                numsize = 32
            else:
                numsize = int(numsize)
                if (numsize & 7) != 0 or numsize > 256 or numsize < 0:
                    raise SolidityTypeError("invalid given-datatype: " + para_type)
                numsize >>= 2
            if isinstance(para, str):
                if not hex_match.match(para) and not hex_match_withprefix.match(para):
                    raise TypeError("invalid hexstring" + para + " for initializing datatype " + para_type)
            elif isinstance(para, int):
                if para < 0:
                    negative_flag = 'f'
                    numstr = hex(INTM[numsize >> 1] + para)[2:]
                else:
                    numstr = hex(numstr)[2:]
            else:
                raise TypeError("unexpected type " + type(para) + " for initializing datatype " + para_type)
            if len(numstr) > numsize:
                raise OverflowError("too large number " + str(para) + " to fill in type" + para_type)
            return negative_flag * (BYTE32_LENGTH - len(numstr)) + numstr
        elif para_type[0:4] == 'uint':
            if isinstance(para, str):
                if not hex_match.match(para) and not hex_match_withprefix.match(para):
                    raise TypeError("invalid hexstring " + para + " for initializing datatype " + para_type)
                if para[1] == 'x':
                    numstr = para[2:]
                else:
                    numstr = para
            elif isinstance(para, int):
                if para < 0:
                    raise ValueError("negative number " + str(para) + " for initializing datatype " + para_type)
                numstr = hex(para)[2:]
            else:
                raise TypeError("unexpected type " + type(para) + " for initializing datatype " + para_type)
            numsize = para_type[4:]
            if numsize == "":
                numsize = 64
            else:
                numsize = int(numsize)
                if (numsize & 7) != 0 or numsize > 256 or numsize < 0:
                    raise SolidityTypeError("invalid datatype: " + para_type)
                numsize >>= 2
            if len(numstr) > numsize:
                raise OverflowError("too large number " + str(para) + " to fill in type " + para_type)
            return '0' * (BYTE32_LENGTH - len(numstr)) + numstr
        elif para_type[0:5] == 'bytes':
            if isinstance(para, bytes):
                para = HexBytes(para).hex()[2:]
            elif isinstance(para, str):
                if not hex_match.match(para) and not hex_match_withprefix.match(para):
                    raise TypeError("not hexstring " + para + " for initializing datatype " + para_type)
                if para[1] == 'x':
                    para = para[2:]
            bytes_size = para_type[5:]
            if bytes_size == "":
                if len(para) & 1:
                    raise Mismatch("odd-length byte-array is invalid")
                return AbiEncoder.encode('uint256', len(para) >> 1) + para + \
                       '0' * ((-len(para)) & MOD6)
            else:
                bytes_size = int(bytes_size)
                if len(para) != (bytes_size << 1):
                    raise Mismatch("parameter " + para + " doesn't match the datatype " + para_type)
                if bytes_size > 32:
                    raise SolidityTypeError("invalid given-datatype " + para_type)
                return para + '0' * ((-len(para)) & MOD6)
        raise SolidityTypeError("unexpected or invalid given-datatype: " + para_type)

    @staticmethod
    def isArrayType(para_type):
        return para_type[-1] == ']' or para_type == 'bytes' or para_type == 'string'

    @staticmethod
    def encodes(para_list, para_type_list):
        if len(para_list) != len(para_type_list):
            raise Mismatch('parameters mismatch with parameters_type_list')
        args_count, args_head, args_arrays = (len(para_type_list) << 5), "", ""

        for para_type, para in zip(para_type_list, para_list):
            ret = AbiEncoder.encode(para_type, para)
            if AbiEncoder.isArrayType(para_type):
                args_head += AbiEncoder.encode('uint256', args_count)
                args_arrays += ret
                args_count += (len(ret) >> 1)
            else:
                args_head += ret
        return args_head + args_arrays


class AbiDecoder:
    def __init__(self):
        pass

    @staticmethod
    def decode(ret_type, raw_ret):
        if ret_type == 'address':
            return AbiDecoder.decode('uint160', raw_ret)
        elif ret_type == 'byte':
            return AbiDecoder.decode('bytes1', raw_ret)
        elif ret_type == 'bool':
            return AbiDecoder.decode('uint8', raw_ret) != 0
        elif ret_type[-1] == ']':  # Array
            array_type, array_size = ret_type[:-1].split('[')
            if array_size != "":
                print("TODO array-type:", ret_type)
                pass
            else:
                raise SolidityTypeError("unsupported atom-solidity type" + ret_type)
        elif ret_type[0:3] == 'int':
            if raw_ret[0] == 'f':
                return int(raw_ret, 16) - INTM[32]
            return int(raw_ret, 16)
        elif ret_type[0:4] == 'uint':
            return int(raw_ret, 16)
        elif ret_type[0:5] == 'bytes':
            bytes_size = int(ret_type[5:])
            if bytes_size == "":
                raise SolidityTypeError("unsupported atom-solidity type: bytes")
            return HexBytes(raw_ret[0:(bytes_size << 1)])
        elif ret_type == 'string':
            raise SolidityTypeError("unsupported atom-solidity type: string")

        raise SolidityTypeError("unexpected or invalid given-datatype: " + ret_type)

    @staticmethod
    def isArrayType(para_type):
        return para_type[-1] == ']' or para_type == 'bytes' or para_type == 'string'

    @staticmethod
    def decodeArray(ret_type, raw_rets):
        if 64 > len(raw_rets):
            raise OverflowError("superflours decode for array: input " + str(len(raw_rets)) + " but expect at least 64")
        if ret_type == 'bytes':
            ret_size = AbiDecoder.decode('uint256', raw_rets[0:64])
            if 64 + (ret_size << 1) > len(raw_rets):
                raise OverflowError("superflours decode for array: input " + str(len(raw_rets)) + \
                                    " but expect at least " + str(64 + (ret_size << 1)))
            return HexBytes(raw_rets[64:64 + (ret_size << 1)])
        elif ret_type == 'string':
            ret_size = AbiDecoder.decode('uint256', raw_rets[0:64])
            if 64 + (ret_size << 1) > len(raw_rets):
                raise OverflowError("superflours decode for array: input " + str(len(raw_rets)) + \
                                    " but expect at least " + str(64 + (ret_size << 1)))
            return raw_rets[64:64 + (ret_size << 1)].encode('utf-8')
        else:
            if ret_type[-2:] == '[]':
                if ret_type[-3] == ']':
                    print("TODO array-type:", ret_type)
                    return
                ret_size = AbiDecoder.decode('uint256', raw_rets[0:64])
                if 64 + (ret_size << 6) > len(raw_rets):
                    raise OverflowError("superflours decode for array: input " + str(len(raw_rets)) + \
                                        " but expect at least " + str(64 + (ret_size << 1)))
                return [
                    AbiDecoder.decode(ret_type[:-2], raw_rets[(idx << 6):(idx + 1) << 6])
                    for idx in range(1, ret_size + 1)
                ]
            else:
                print("TODO array-type:", ret_type)
                return

    @staticmethod
    def decodes(raw_rets, rets_type_list):
        if len(raw_rets) & MOD6:
            raise ValueError("data damaged")
        rets, ret_counter = [], 0

        for ret_type in rets_type_list:
            if AbiDecoder.isArrayType(ret_type):
                ret = AbiDecoder.decodeArray(
                    ret_type,
                    raw_rets[(AbiDecoder.decode('uint256', raw_rets[ret_counter:ret_counter + 64]) << 1):]
                )
                rets.append(ret)
            else:
                ret = AbiDecoder.decode(ret_type, raw_rets[ret_counter:ret_counter + 64])
                rets.append(ret)
            ret_counter += 64
        return rets


class SignatrueVerifier:
    def __init__(self):
        pass

    @staticmethod
    def initEthSignature(raw_signature):
        return KeyAPI.Signature(HexBytes(hex(int(raw_signature, 16) - 27)))

    @staticmethod
    def initSignature(sig):
        if isinstance(sig, str):
            if sig[-2:] != '01':
                sig = hex(int(sig, 16) - 27)
            try:
                sig = KeyAPI.Signature(HexBytes(sig))
            except Exception:
                raise TypeError(type(sig) + "is not verifiable signature")
        elif isinstance(sig, bytes) or isinstance(sig, HexBytes):
            if sig[-1] != 1:
                sig = bytestoint(sig)
                sig -= 27
            sig = HexBytes(hex(sig))
            try:
                sig = KeyAPI.Signature(sig)
            except Exception:
                raise TypeError(type(sig) + "is not verifiable signature")
        elif not isinstance(sig, KeyAPI.Signature):
            raise TypeError(type(sig) + "is not verifiable signature")
        return sig

    @staticmethod
    def verifyByRawMessage(sig, msg, addr):
        if isinstance(msg, str):
            msg = bytes(msg.encode(ENC))
        msg = ETHSIGN_HEADER + bytes(str(len(msg)).encode(ENC)) + msg
        sig = SignatrueVerifier.initSignature(sig)
        return sig.recover_public_key_from_msg(msg).to_checksum_address() == Web3.toChecksumAddress(addr)

    @staticmethod
    def verifyByHashedMessage(sig, msg, addr):
        sig = SignatrueVerifier.initSignature(sig)
        return sig.recover_public_key_from_msg_hash(msg).to_checksum_address() == Web3.toChecksumAddress(addr)


if __name__ == '__main__':
    type_list = ['uint256', 'bytes2[]', 'bytes2[]', 'uint256', 'int256', 'bytes2[]']
    encodetest = AbiEncoder.encodes([123123, ['0x0142'], ['0x1420'], 1123, -1, ["0x1042"]], type_list)
    print("1234567890abcdef" * 0x30)  # 0x30 * 8 = 0x180
    print(encodetest)
    print(AbiDecoder.decodes(encodetest, type_list))
    # print(AbiEncoder.encodes(['tannekawaii', 'daisuki'], ['string', 'string']))
    # print(hex(INTM[32] - 2))
    # print(AbiEncoder.encode('string', "tannekawaii"))
    # print(AbiEncoder.encode('int256', -1))
    # print(AbiEncoder.encode('int32', -1))
    # print(AbiEncoder.encode('uint256', 1))
    # print(AbiEncoder.encode('int32', 123))
    # print(AbiEncoder.encode('byte', "0x01"))
    # print(AbiEncoder.encode('bytes1', "0x01"))
    # print(AbiEncoder.encode('bytes2', "0x0102"))
    # print(AbiEncoder.encode('bytes3', "0x000102"))
    # print(AbiEncoder.encode('bytes', "0x000102030405060708090a0b0c0d0e0f000102030405060708090a0b0c0d0e0f00010203040506
    # 0708090a0b0c0d0e0f000102030405060708090a0b0c0d0e0f"))
    # print(HexBytes(sliceloc(b'\x01', 1, 8)).hex())
    # print(HexBytes(slicelocation(b'\x01', 1, 8)).hex())
    # print(HexBytes(slicelocation(1, 1, 16)).hex())
    # print(HexBytes(slicelocation("1", 1, 8)).hex())
    # print(HexBytes(slicelocation("0x1", 1, 8)).hex())
    # print(HexBytes(maploc(b'\x00', b'\x00')).hex())

# 1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
# data                                                             # byte
# 000000000000000000000000000000000000000000000000000000000001e0f3 # 00
# 00000000000000000000000000000000000000000000000000000000000000c0 # 20
# 0000000000000000000000000000000000000000000000000000000000000100 # 40
# 0000000000000000000000000000000000000000000000000000000000000463 # 60
# ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff # 80
# 0000000000000000000000000000000000000000000000000000000000000140 # a0
# 0000000000000000000000000000000000000000000000000000000000000001 # c0
# 1402000000000000000000000000000000000000000000000000000000000000 # e0
# 0000000000000000000000000000000000000000000000000000000000000001 # 100
# 1420000000000000000000000000000000000000000000000000000000000000 # 120
# 0000000000000000000000000000000000000000000000000000000000000001 # 140
# 1042000000000000000000000000000000000000000000000000000000000000 # 160
#                                                                    180
