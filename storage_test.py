
from uiputils.eth import ServiceStart
from uiputils.cast import uint32string
from web3 import Web3
from eth_hash.auto import keccak
from hexbytes import  HexBytes

addr = Web3.toChecksumAddress("0x97470438563859d09e744bcb136e8e298edc9ca9")


if __name__ == '__main__':
    web3h = ServiceStart.startweb3('http://127.0.0.1:8545')
    ask_string = keccak(HexBytes(uint32string(0))+HexBytes(uint32string(0)))
    ask_string = HexBytes(ask_string).hex()
    print(ask_string)
    print(HexBytes(web3h.eth.getStorageAt(addr, ask_string)).hex())

# 0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563
# 0xb1b278718f96e5394d19dcec6fb533b19e1d47c5d05b9411f37eed2f7b10f5c2