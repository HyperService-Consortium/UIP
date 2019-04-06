
# ethereum modules
from hexbytes import HexBytes
from web3 import Web3

# eth modules
from uiputils.contract.wrapped_contract_function import ContractFunctionClient
from uiputils.ethtools import ServiceStart, FileLoad


class EthContract:
    # return a contract that can transact with web3

    def __init__(self, web3_addr, contract_addr="", contract_abi=None, contract_bytecode=None, timeout=30):

        web3 = ServiceStart.startweb3(web3_addr)
        contract_abi = FileLoad.getabi(contract_abi)
        contract_bytecode = FileLoad.getbytecode(contract_bytecode)

        if contract_addr != "":
            self.handle = web3.eth.contract(
                Web3.toChecksumAddress(contract_addr),
                abi=contract_abi,
                bytecode=contract_bytecode
            )
        else:
            self.handle = web3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)

        self.timeout = timeout
        self.web3 = web3
        self.address = self.handle.address
        self.abi = self.handle.abi
        self.bytecode = self.handle.bytecode
        self.functions = self.handle.functions

    def func(self, funcname, *args):
        # call a contract function
        return self.handle.functions[funcname](*args).call()

    def funct(self, funcname, tx_head, *args, timeout=None, gasuse=None):
        # transact a contract function
        to_send_tx_head = tx_head
        if timeout is None:
            timeout = self.timeout
        if gasuse is not None:
            # is it necessary to deep-copy?
            to_send_tx_head = tx_head.copy()
            to_send_tx_head['gas'] = gasuse
        tx_rec = self.handle.functions[funcname](*args).transact(to_send_tx_head)
        return self.web3.eth.waitForTransactionReceipt(HexBytes(tx_rec).hex(), timeout=timeout)

    def lazyfunct(self, funcname, tx_head, *args, timeout=None, gasuse=None):
        to_send_tx_head = tx_head
        if timeout is None:
            timeout = self.timeout
        if gasuse is not None:
            # is it necessary to deep-copy?
            to_send_tx_head = tx_head.copy()
            to_send_tx_head['gas'] = gasuse
        func = self.handle.functions[funcname](*args)
        return ContractFunctionClient(
            # bounded_contract_function
            func.transact,
            func.call,
            # wait_catch
            self.web3.eth.waitForTransactionReceipt,
            to_send_tx_head,
            timeout
        )

    def funcs(self):
        # return all functions in self.abi
        return self.handle.all_functions()
