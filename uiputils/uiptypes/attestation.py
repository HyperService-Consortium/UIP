
import rlp
import json


class Attestation(object):
    """
    hashable Attestation

    Attestation = [Content; Signature]
        eg. [
            [b"{tilde_T: content}", \x01, \x07, \x1F],
            [[\x01\x02...\x65, 0x12345678], [\x65\x64...\x01, 0x87654321]]
        ]

    Content = [rlped-executable_Transactoin(Bytes), State(Byte1), SessionID(Bytes), TransactionID(Bytes)]
    Signature = (signature, identification)[], signature: Bytes65 = r: Bytes32, s: Bytes32, v: Byte1

    the difference between rlped-executable_Transaction and TransactionIntent is that:
        eg. tilde_T = {from: 0x12345678, to: 0x87654321, data: 0x23333333, 123, 456}
                  T = {from: 0x12345678, to: 0x87654321, data: 0x23333333, chainX::storage['contract::X']['key'], 456}

    hash(Attestation): Bytes32 = keccak256(rlp.encode(Attestaion))

    signature = eth_sign_header + len(hash(Attestaion)) + hash(Attestation)

    identification:
        recover (hash(Content; Signature[0...i-1]), signature[i]) == identification[i]

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
        return Attestation.recover_content(atte_list[0]), Attestation.recover_signature(atte_list)

    @staticmethod
    def recover_content(content_list: list):
        return content_list

    @staticmethod
    def recover_signature(atte_list: list):
        pass


if __name__ == '__main__':
    # atte = Attestation(name='tan ne')
    # print(atte['name'])
