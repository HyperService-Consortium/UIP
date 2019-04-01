
# ethereum modules
from hexbytes import HexBytes
from web3 import Web3
from web3.utils.threads import Timeout as Web3Timeout

# eth modules
from uiputils.ethtools import ServiceStart, FileLoad


class EthContract:
    # return a contract that can transact with web3

    class WrapedContractFunction:
        def __init__(self, bounded_contract_function, wait_catch=None, tx=None, timeout=10):
            self.func = bounded_contract_function
            self.timeout = timeout
            self.wait_catch = wait_catch
            self.tx = tx
            print(self.tx)
            self.tx_resp = None

        def transact(self):
            self.tx_resp = HexBytes(self.func.transact(self.tx)).hex()

        def call(self):
            self.func.call()

        def wait(self, timeout=None):
            if self.tx_resp is None:
                raise LookupError("nothing to wait")
            if self.wait_catch is None:
                raise IndexError("catch-function doesn't exist")
            try:
                if timeout:
                    return self.wait_catch(self.tx_resp, timeout)
                else:
                    return self.wait_catch(self.tx_resp, self.timeout)
            except Web3Timeout:
                return None
            except Exception as e:
                raise e

        def loop_and_wait(self):
            while True:
                try:
                    tx_result = self.wait(timeout=998244353)
                    if tx_result is None:
                        continue
                    return tx_result
                except Exception as e:
                    raise e

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
        return EthContract.WrapedContractFunction(
            # bounded_contract_function
            self.handle.functions[funcname](*args),
            # wait_catch
            self.web3.eth.waitForTransactionReceipt,
            to_send_tx_head,
            timeout
        )

    def funcs(self):
        # return all functions in self.abi
        return self.handle.all_functions()
