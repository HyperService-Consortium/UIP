
from .loadfile import FileLoad
from .startservice import ServiceStart
from hexbytes import HexBytes
from .tools import Prover
# import time


class Contract:
    # return a contract that can transact with web3
    def __init__(self, web3_addr, contract_addr="", contract_abi=None, contract_bytecode=None):

        web3 = ServiceStart.startweb3(web3_addr)
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

    def funct(self, funcname, tx, *args):
        # transact a contract function
        tx_rec = self.handle.functions[funcname](*args).transact(tx)
        return self.web3.eth.waitForTransactionReceipt(HexBytes(tx_rec).hex(), timeout=10)

    def funcs(self):
        # return all functions in self.abi
        return self.handle.all_functions()


SLOT_WAITING_QUEUE = 0
SLOT_VOTEDPOINTER = 5

class NetStatusBlockchain:
    # Prot NSB in uip
    def __init__(self, host_addr, nsb_addr, nsb_abi_addr, eth_db_addr, nsb_bytecode_addr=None):
        # , nsb_db_addr):
        self.handle = Contract(host_addr, nsb_addr, nsb_abi_addr, nsb_bytecode_addr)
        self.web3 = self.handle.web3
        self.address = self.handle.address
        print("test, so not linking to", eth_db_addr)
        # self.prover = Prover(eth_db_addr)
        pass

    def getQueueR(self):
        # return Queue[L,R) 's R
        return self.web3.eth.getStorageAt(self.address, SLOT_WAITING_QUEUE)

    def getQueueL(self):
        # return Queue[L,R) 's L
        return self.web3.eth.getStorageAt(self.address, SLOT_VOTEDPOINTER)

    def singleProve(self):
        pass

    def work(self, work_time):
        pass
