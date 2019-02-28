import json
# import web3
from web3 import Web3
from hexbytes import HexBytes
# from solc import compile_standard

# compiled_sol = compile_standard
#     'language': 'Solidity',
#     'sources': {
#         'broker': {
#             "urls":[
#                 "./broker.sol"
#             ]
#         }
#     }
# }, allow_paths="./,", abi=True, bin=True, source_files=["broker.sol"]
# )
# compiled_sol = compile_source("./broker.sol", allow_empty=False)

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545", request_kwargs={'timeout': 10}))

broker_addr = Web3.toChecksumAddress("0xd7ea2b03da511799eb0c5a28989cf5268c869311")
broker_abi_addr = "broker_abi"
broker_bytecode_addr = "broker_bytecode"

nsb_addr = Web3.toChecksumAddress("0x9d013da6392577830100b8e8d366196008ed19aa")
nsb_abi_addr = "./nsb/nsb.abi"
nsb_bytecode_addr = "./nsb/nsb.bin"

class FileLoad(object):
    def __int__(self):
        pass

    @staticmethod
    def getabi(contract_abi):
        if isinstance(contract_abi, str):
            with open(contract_abi, "r") as abifile:
                return json.load(abifile)
        else:
            return contract_abi

    @staticmethod
    def getbytecode(contract_bytecode):
        if isinstance(contract_bytecode, str):
            with open(contract_bytecode, "rb") as bytecodefile:
                return bytecodefile.read()
        else:
            return contract_bytecode


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
