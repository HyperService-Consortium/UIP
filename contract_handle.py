
from web3 import Web3
from uiputils.eth.ethtypes import NetStatusBlockchain
from hexbytes import HexBytes
import json
# import plyvel


host_addr = "http://127.0.0.1:8545"

broker_addr = Web3.toChecksumAddress("0xd7ea2b03da511799eb0c5a28989cf5268c869311")
broker_abi_dir = "broker_abi"
broker_bytecode_dir = "broker_bytecode"

eth_base_addr = Web3.toChecksumAddress("0x7019fa779024c0a0eac1d8475733eefe10a49f3b")

nsb_addr = Web3.toChecksumAddress("0x43710274daadce0d8bdfe7ae6495140ea83cda6a")
# ("0x076122c56613fc1e3ae97d715ca7cb6a35a934c6")

nsb_abi_dir = "./nsb/nsb.abi"
nsb_bytecode_dir = "./nsb/nsb.bin"
nsb_db_dir = "./nsb/actiondata"
tx = {
    "from": eth_base_addr,
    "gas": hex(400000)
}

if __name__ == '__main__':
    nsbt = NetStatusBlockchain(eth_base_addr, host_addr, nsb_addr, nsb_abi_dir, "", nsb_bytecode_dir=nsb_bytecode_dir)
    nsb = nsbt.handle

    # 0x64e604787cbf194841e7b68d7cd28786f6c9a0a3ab9f8b0a0e87cb4387ab0107
    # print(HexBytes(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00C').hex())

    #  = nsbt.addAction("123456781234567812345678123456781")
    # print(keccakhash)

    # print(nsbt.getAction("0xbc7e08dc633826033d13aaab04b8e2196cd944351ea0046dae500d4e027939e2"))

    # print(HexBytes(nsbt.getQueueL()).hex(), HexBytes(nsbt.getQueueR()).hex())
    # nsbt.watchProofPool()

    # print(nsb_addr)
    #
    # print(nsb.funcs())
    #
    # # print(nsb.func('isOwner', Web3.toChecksumAddress("0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e")))
    #
    # # print(nsb.funct('addOwner', tx, Web3.toChecksumAddress("0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e")))
    #
    # # print(nsb.func('isOwner', Web3.toChecksumAddress("0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e")))
    #
    # print(nsb.funct('addMerkleProof', tx, "A", "933b2499f931cef309f61259914d250c69446f55dcd9a6e85cebf0aed214ef36",
    #                 "0275b7a638427703f0dbe7bb9bbf987a2551717b34e79f33b5b1008d1fa01db9",
    #                 "0100000000000000000000000000000000000000000000000000000000000000"))
    #
    # print(nsb.funct('addMerkleProof', tx, "ABCDEFG", "123b2499f931cef309f61259914d250c69446f55dcd9a6e85cebf0aed214ef36",
    #                 "4565b7a638427703f0dbe7bb9bbf987a2551717b34e79f33b5b1008d1fa01db9",
    #                 "7890000000000000000000000000000000000000000000000000000000000000"))
    #
    # print(nsb.funct('addMerkleProof', tx, "123456781234567812345678123456781", "123b2499f931cef309f61259914d250c69446f55dcd9a6e85cebf0aed214ef36",
    #                 "4565b7a638427703f0dbe7bb9bbf987a2551717b34e79f33b5b1008d1fa01db9",
    #                 "7890000000000000000000000000000000000000000000000000000000000000"))


# 0x0000000000000000000000000000000000000000000000000000000000000043

# 64*16bit=1024bit=128bytes
# 0000000000000000000000000000000000000000000000000000000000000040
# 40=4*16=64?,not ,prefix,or:0(uint256),4(list)
# 0000000000000000000000000000000000000000000000000000000000000001(require)
# 0000000000000000000000000000000000000000000000000000000000000001(listlength)
# 000000000000000000000000e1300d8ea0909faa764c316436ad0ece571f62b2(address)