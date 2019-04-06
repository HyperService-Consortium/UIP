from typing import List

import rlp
import json
from uiputils.transaction import StateType
from uiputils.uiptools.cast import bytestoint
from uiputils.errors import DecodeFail, VerificationError
from uiputils.ethtools import SignatureVerifier
from eth_keys import KeyAPI
from hexbytes import HexBytes
from eth_keys.datatypes import PrivateKey
from eth_hash.auto import keccak
from eth_utils import to_normalized_address
from uiputils.config import ETHSIGN_HEADER


# constant
ENC = 'utf-8'


class Attestation(object):
    """
    hashable Attestation

    Attestation = [Content; Signature]
        eg. [
            [b"{tilde_T:content}", \x01, \x07, \x1F],
            [[\x01\x02...\x65, 0x12345678], [\x65\x64...\x01, 0x87654321]]
        ]

    Content = [executable_Transactoin(Bytes), State(Byte1), SessionID(Bytes), TransactionID(Bytes)]
    Signature = (signature, identification)[], signature: Bytes65 = r: Bytes32, s: Bytes32, v: Byte1

    the difference between executable_Transaction and TransactionIntent is that:
        eg. tilde_T = {from: 0x12345678, to: 0x87654321, data: 0x23333333, 123, 456}
                  T = {from: 0x12345678, to: 0x87654321, data: 0x23333333, chainX::storage['contract::X']['key'], 456}

    hash(Attestation): Bytes32 = keccak256(rlp.encode(Attestaion))

    signature = eth_sign_header + len(hash(Attestaion)) + hash(Attestation)

    identification:
        recover (rlp.encode([Content; Signature[0...i-1]]), signature[i]) == identification[i]

    on_chain Attestation: (hashed_Attestation, signature[i])
    """

    def __init__(self, atte_list: bytes or list):
        if isinstance(atte_list, bytes):
            atte_list = rlp.decode(atte_list)
        print(atte_list)
        self.content, self.signatures = Attestation.recover_atte(atte_list)

    @staticmethod
    def recover_atte(atte_list: list):
        if len(atte_list) != 2:
            raise ValueError(
                "the format of Attestation must be [Content, Signature], but you give a length of " +
                str(len(atte_list)) +
                " ?"
            )
        # first right, then left (because of reference variable in python)
        right_res = Attestation.recover_signatures(atte_list)
        left_res = Attestation.recover_content(atte_list[0])
        return left_res, right_res

    def sign_and_encode(self, signature_pair):
        self.signatures.append(signature_pair)
        return self.encode()

    def encode(self):
        return rlp.encode([
            Attestation.encode_content(self.content),
            Attestation.encode_signatures(self.signatures)
        ])

    @staticmethod
    def recover_content(content_list: list):
        if len(content_list) != 4:
            raise ValueError(
                "the format of Attestation must be [T, State, Sid, Tid], but you give a length of " +
                str(len(content_list)) +
                " ?"
            )
        try:
            content_list[0] = json.loads(content_list[0].decode(ENC))
            content_list[1] = StateType(bytestoint(content_list[1]))
            content_list[2] = bytestoint(content_list[2])
            content_list[3] = bytestoint(content_list[3])
        except Exception as e:
            raise DecodeFail(" failed when recovering content, " + str(e))
        return content_list

    @staticmethod
    def recover_signatures(atte_list: list):
        left_list, res_list = [], []
        for sig, addr in atte_list[1]:
            rlped_data = rlp.encode([atte_list[0], left_list])
            left_list.append([sig, addr])
            print(HexBytes(sig).hex())
            sig = SignatureVerifier.init_signature(HexBytes(sig).hex())
            addr = addr.decode(ENC)
            res_list.append([sig, addr])
            if not SignatureVerifier.verify_by_raw_message(sig, keccak(rlped_data), addr):
                raise VerificationError(
                    "wrong signature when verifying: " +
                    "\ncontent: " + HexBytes(rlped_data).hex() +
                    "\nsignature: " + sig.to_hex() +
                    "\naddress: " + addr
                )
        return res_list

    @staticmethod
    def encode_content(content_list: list):
        return [
            json.dumps(content_list[0], sort_keys=True).encode('utf-8'),
            HexBytes(hex(content_list[1].value)),
            HexBytes(hex(content_list[2])),
            HexBytes(hex(content_list[3]))
        ]

    @staticmethod
    def encode_signatures(signatures_list):
        return [[sig.to_bytes(), addr.encode(ENC)] for sig, addr in signatures_list]

    def hash(self):
        return keccak(self.encode())


if __name__ == '__main__':
    pbx = PrivateKey(
        b'\x12\x34\x56\x78\x12\x34\x56\x78\x12\x34\x56\x78\x12\x34\x56\x78'
        b'\x12\x34\x56\x78\x12\x34\x56\x78\x12\x34\x56\x78\x12\x34\x56\x78'
    )
    pby = PrivateKey(
        b'\x23\x45\x67\x89\x23\x45\x67\x89\x23\x45\x67\x89\x23\x45\x67\x89'
        b'\x23\x45\x67\x89\x23\x45\x67\x89\x23\x45\x67\x89\x23\x45\x67\x89'
    )
    print(pbx.public_key.to_address().encode('utf-8'))
    content = [
        bytes(json.dumps(
            {"from": "0x12345678", "to": "0x87654321", "data": "..."},
            sort_keys=True
        ).encode('utf-8')),
        b'\x01',
        b'\x02',
        b'\x03'
    ]
    signaturex = [
        pbx.sign_msg(
            ETHSIGN_HEADER + b'\x33\x32' + keccak(rlp.encode([content, []]))
        ).to_bytes(),
        pbx.public_key.to_address()
    ]
    rlped_datax = rlp.encode([content, [signaturex]])
    print(rlped_datax)
    import time
    time.sleep(1)
    attex = Attestation(rlped_datax)
    print(attex.content, attex.signatures)
    print(attex.encode() == rlped_datax)
    attex.sign_and_encode([
        pby.sign_msg(
            ETHSIGN_HEADER + b'\x33\x32' + attex.hash()
        ),
        pby.public_key.to_address()
    ])
    rlped_datay = attex.encode()
    attey = Attestation(rlped_datay)
    print(attey.content, attey.signatures)
    print(attey.encode() == rlped_datay)
