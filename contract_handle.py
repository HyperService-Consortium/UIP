
from web3 import Web3
from hexbytes import HexBytes
from uiputils.loadfile import FileLoad


web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545", request_kwargs={'timeout': 10}))

broker_addr = Web3.toChecksumAddress("0xd7ea2b03da511799eb0c5a28989cf5268c869311")
broker_abi_addr = "broker_abi"
broker_bytecode_addr = "broker_bytecode"

nsb_addr = Web3.toChecksumAddress("0x4c8941bae3f7db6837f7b0bcad76d5fe416d9eb9")
nsb_abi_addr = "./nsb/nsb.abi"
nsb_bytecode_addr = "./nsb/nsb.bin"


class Contract:
    def __init__(self, contract_addr="", contract_abi=None, contract_bytecode=None):

        self.addr = contract_addr
        contract_abi = FileLoad.getabi(contract_abi)
        contract_bytecode = FileLoad.getbytecode(contract_bytecode)

        if contract_addr != "":
            self.handle = web3.eth.contract(contract_addr, abi=contract_abi, bytecode=contract_bytecode)
        else:
            self.handle = web3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)

    def func(self, funcname, *args):
        return self.handle.functions[funcname](*args).call()


if __name__ == '__main__' :
    # print(compiled_sol)
    print(web3.eth)
    print(web3.eth.coinbase)
    print(web3.eth.accounts)
    print(HexBytes(web3.eth.getStorageAt(broker_addr, "0x0", "latest")).hex())
    # broker = Contract(broker_addr, broker_abi_addr, broker_bytecode_addr)
    # print(broker.handle.all_functions())
    # print(broker.func('getGenuineValue'))
    # print(broker.func('isOwner',Web3.toChecksumAddress(broker_addr)))
    nsb = Contract(nsb_addr, nsb_abi_addr, nsb_bytecode_addr)
    print(nsb.handle.all_functions())
    print(nsb.func('isOwner', Web3.toChecksumAddress("0xe1300d8ea0909faa764c316436ad0ece571f62b2")))

	
# 64*16bit=1024bit=128bytes
# 0000000000000000000000000000000000000000000000000000000000000040
# 40=4*16=64?,not ,prefix,or:0(uint256),4(list)
# 0000000000000000000000000000000000000000000000000000000000000001(require)
# 0000000000000000000000000000000000000000000000000000000000000001(listlength)
# 000000000000000000000000e1300d8ea0909faa764c316436ad0ece571f62b2(address)