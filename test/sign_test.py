
# ethereum modules
from eth_hash.auto import keccak
from hexbytes import HexBytes
from eth_keys import KeyAPI

# eth modules
from uiputils.ethtools import SignatureVerifier

# config
from uiputils.config import ETHSIGN_HEADER
signer = 0x7019fa779024c0a0eac1d8475733eefe10a49f3b
eth_signature = "0x4d87ae548152fa6eb06c502579347277bce151616ff76ea4663338119c4e36665" + \
                  "9ffd74f5cf75f9f27fc1f3d87dd43f08cb7c535186de3f7bffd51536742e48d1c"
raw_msg = b"123"

if __name__ == '__main__':
    raw_signature = hex(int(eth_signature, 16) - 27)
    msg = ETHSIGN_HEADER + bytes(str(len(raw_msg)).encode('utf-8')) + raw_msg
    msghash = keccak(msg)
    print(msg, HexBytes(msghash).hex())
    # print(HexBytes(msg).hex())

    print(SignatureVerifier.verify_by_raw_message(eth_signature, raw_msg, signer))

    print(SignatureVerifier.verify_by_raw_message(raw_signature, raw_msg, signer))

    print(SignatureVerifier.verify_by_hashed_message(eth_signature, msghash, signer))

    print(SignatureVerifier.verify_by_hashed_message(raw_signature, msghash, signer))

    sig = KeyAPI.Signature(HexBytes(raw_signature))

    print(sig.recover_public_key_from_msg(msg).to_checksum_address())

    print(sig.recover_public_key_from_msg_hash(msghash).to_checksum_address())



