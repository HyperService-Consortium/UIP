
from web3 import Web3
from uiputils.eth.types import NetStatusBlockchain
# import plyvel


host_addr = "http://127.0.0.1:8545"

broker_addr = Web3.toChecksumAddress("0xd7ea2b03da511799eb0c5a28989cf5268c869311")
broker_abi_addr = "broker_abi"
broker_bytecode_addr = "broker_bytecode"

nsb_addr = Web3.toChecksumAddress("0x076122c56613fc1e3ae97d715ca7cb6a35a934c6")
# ("0x4c8941bae3f7db6837f7b0bcad76d5fe416d9eb9")
nsb_abi_addr = "./nsb/nsb.abi"
nsb_bytecode_addr = "./nsb/nsb.bin"
nsb_db_addr = "./nsb/actiondata"


if __name__ == '__main__':
    nsbt = NetStatusBlockchain(host_addr, nsb_addr, nsb_abi_addr, nsb_bytecode_addr)
    nsb = nsbt.handle

    print(nsb.funcs())

    print(nsb.functions.isOwner(Web3.toChecksumAddress("0xe1300d8ea0909faa764c316436ad0ece571f62b2")).call())
    print(nsb.func('isOwner', Web3.toChecksumAddress("0xe1300d8ea0909faa764c316436ad0ece571f62b2")))

	
# 64*16bit=1024bit=128bytes
# 0000000000000000000000000000000000000000000000000000000000000040
# 40=4*16=64?,not ,prefix,or:0(uint256),4(list)
# 0000000000000000000000000000000000000000000000000000000000000001(require)
# 0000000000000000000000000000000000000000000000000000000000000001(listlength)
# 000000000000000000000000e1300d8ea0909faa764c316436ad0ece571f62b2(address)