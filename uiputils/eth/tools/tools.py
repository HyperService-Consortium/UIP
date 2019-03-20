
# python modules

from uiputils.cast import bytestoint

# ethereum modules
from hexbytes import HexBytes
from eth_keys import KeyAPI
from web3 import Web3

# self-package modules

# config
from uiputils.config import ETHSIGN_HEADER

# constant
ENC = "utf-8"
MOD256 = (1 << 256) - 1


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
    pass
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
