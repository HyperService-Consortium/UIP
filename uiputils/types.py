
'some cast method'

__author__ = 'Myriad Dreamin'

from uiputils.loadfile import FileLoad

class Contract:
    def __init__(self, web3, contract_addr="", contract_abi=None, contract_bytecode=None):

        self.addr = contract_addr
        self.web3 = web3
        contract_abi = FileLoad.getabi(contract_abi)
        contract_bytecode = FileLoad.getbytecode(contract_bytecode)

        if contract_addr != "":
            self.handle = web3.eth.contract(contract_addr, abi=contract_abi, bytecode=contract_bytecode)
        else:
            self.handle = web3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)

    def func(self, funcname, *args):
        return self.handle.functions[funcname](*args).call()