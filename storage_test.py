
from uiputils.eth import ServiceStart
from web3 import Web3
from uiputils.eth import JsonRPC
from hexbytes import HexBytes
from uiputils.eth.tools import slicelocation, maplocation
from uiputils.eth.ethtypes import NetStatusBlockchain

EDB_PATH = "D:/Go Ethereum/data/geth/chaindata"
url = "http://127.0.0.1:8545"
HTTP_HEADER = {'Content-Type': 'application/json'}
nsb_addr = "0x43710274DaADCe0D8bDFE7ae6495140eA83CDA6a"
# ("0x076122c56613fc1e3ae97d715ca7cb6a35a934c6")

nsb_abi_addr = "./nsb/nsb.abi"
nsb_bytecode_addr = "./nsb/nsb.bin"
nsb_db_addr = "./nsb/actiondata"
if __name__ == '__main__':
    web3h = ServiceStart.startweb3(url)
    # key = 0
    nsbt = NetStatusBlockchain(url, nsb_addr, nsb_abi_addr, EDB_PATH, nsb_bytecode_addr)
    nsb = nsbt.handle

    # print(JsonRPC.send(url, HTTP_HEADER, JsonRPC.ethGetProof(nsb_addr, ["0x0"], "latest"))
    #       ['result']['storageProof'][0]['value'])
    #
    print(nsb.funcs())
    # idx:  0
    #     block_address A
    #     storageHash 0x933b2499f931cef309f61259914d250c69446f55dcd9a6e85cebf0aed214ef36
    #     key 0x0275b7a638427703f0dbe7bb9bbf987a2551717b34e79f33b5b1008d1fa01db9
    #     value 0x0100000000000000000000000000000000000000000000000000000000000000
    # idx:  1
    #     block_address B
    #     storageHash 0x933b2499f931cef309f61259914d250c69446f55dcd9a6e85cebf0aed214ef36
    #     key 0x0275b7a638427703f0dbe7bb9bbf987a2551717b34e79f33b5b1008d1fa01db9
    #     value 0x0100000000000000000000000000000000000000000000000000000000000000

    # print(HexBytes(web3h.eth.getStorageAt(nsb_addr, ask_string)).hex())
    #
    # print(HexBytes(nsb.func('waitingVerifyProof', 1)).hex())
    #
    # ask_string = HexBytes(slicelocation(0, 1, 1)).hex()
    # print("cac", ask_string)
    # # key = 0x29...
    #
    # print(JsonRPC.send(url, HTTP_HEADER, JsonRPC.ethGetProof(nsb_addr, [ask_string], "latest"))
    #       ['result']['storageProof'][0]['value'])
    # print(HexBytes(web3h.eth.getStorageAt(nsb_addr, ask_string)).hex())
    #
    # # hash of proof[1] = 0xe0b1f574a33e073946d003d8ab3727dd80ccac1d718e04e168b5f0a564e6b4bc
    #
    # print(nsb.func('proofPointer', "e0b1f574a33e073946d003d8ab3727dd80ccac1d718e04e168b5f0a564e6b4bc"))
    #
    # ask_string = HexBytes(maplocation(3, "e0b1f574a33e073946d003d8ab3727dd80ccac1d718e04e168b5f0a564e6b4bc")).hex()
    # print("cac", ask_string)
    # # key = 0x29...
    #
    # print(JsonRPC.send(url, HTTP_HEADER, JsonRPC.ethGetProof(nsb_addr, [ask_string], "latest"))
    #       ['result']['storageProof'][0]['value'])
    # print(HexBytes(web3h.eth.getStorageAt(nsb_addr, ask_string)).hex())
