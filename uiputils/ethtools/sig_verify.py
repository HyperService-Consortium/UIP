
# uip modules
from uiputils.uiptools.cast import bytestoint

# ethereum modules
from hexbytes import HexBytes
from eth_keys import KeyAPI
from web3 import Web3

# config
from uiputils.config import ETHSIGN_HEADER

# constant
ENC = "utf-8"


class IdleSignature(bytes):
    def __init__(self, sig):
        super().__init__()
        self.signature = sig

    def bytes(self):
        return self.signature

    def hex(self):
        return self.signature.hex()

    def to_hex(self):
        return self.signature.hex()

    def to_bytes(self):
        return self.signature


class SignatureVerifier:
    def __init__(self):
        pass

    @staticmethod
    def eth_signature(raw_signature):
        return KeyAPI.Signature(HexBytes(hex(int(raw_signature, 16) - 27)))

    @staticmethod
    def init_signature(sig):
        if isinstance(sig, str):
            if sig[0:2] == "0x":
                sig = sig[2:]
            sig = bytes.fromhex(sig)
        return IdleSignature(sig)


        if isinstance(sig, str):
            if sig[-2:] != '01' and sig[-2:] != '00':
                sig = hex(int(sig, 16) - 27)
            try:
                sig = KeyAPI.Signature(HexBytes(sig))
            except Exception:
                raise TypeError(str(type(sig)) + "is not verifiable signature")
        elif isinstance(sig, bytes):
            if sig[-1] != 1 and sig[-1] != 0:
                sig = bytestoint(sig)
                sig -= 27
                sig = HexBytes(hex(sig))
            try:
                sig = KeyAPI.Signature(sig)
            except Exception:
                raise TypeError(str(type(sig)) + "is not verifiable signature")
        elif not isinstance(sig, KeyAPI.Signature):
            raise TypeError(str(type(sig)) + "is not verifiable signature")
        return sig

    @staticmethod
    def verify_by_raw_message(sig, msg, addr):
        if isinstance(msg, str):
            msg = bytes(msg.encode(ENC))
        msg = ETHSIGN_HEADER + bytes(str(len(msg)).encode(ENC)) + msg
        sig = SignatureVerifier.init_signature(sig)
        return sig.recover_public_key_from_msg(msg).to_checksum_address() == Web3.toChecksumAddress(addr)

    @staticmethod
    def verify_by_hashed_message(sig, msg, addr):
        if isinstance(msg, str):
            msg = HexBytes(msg)
        sig = SignatureVerifier.init_signature(sig)
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
