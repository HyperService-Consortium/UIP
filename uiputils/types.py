
'some cast method'

__author__ = 'Myriad Dreamin'

from uiputils.loadfile import FileLoad


class Contract:
    # return a contract that can transact with web3
    def __init__(self, web3, contract_addr="", contract_abi=None, contract_bytecode=None):

        contract_abi = FileLoad.getabi(contract_abi)
        contract_bytecode = FileLoad.getbytecode(contract_bytecode)

        if contract_addr != "":
            self.handle = web3.eth.contract(contract_addr, abi=contract_abi, bytecode=contract_bytecode)
        else:
            self.handle = web3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)

        self.web3 = web3
        self.address = self.handle.address
        self.abi = self.handle.abi
        self.bytecode = self.handle.bytecode
        self.functions = self.handle.functions

    def func(self, funcname, *args):
        # call a contract function
        return self.handle.functions[funcname](*args).call()

    def funcs(self):
        # return all functions in self.abi
        return self.handle.all_functions()
