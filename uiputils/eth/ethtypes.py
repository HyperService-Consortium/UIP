
from .loadfile import FileLoad
from .startservice import ServiceStart
from hexbytes import HexBytes
from uiputils.cast import bytestoint, catint32
from .tools import Prover, LocationTransLator
from collections import namedtuple
# import time


MerkleProof = namedtuple('MerkleProof', 'blockaddr storagehash key value')


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
SLOT_MERKLEPROOFTREE = 6


class NetStatusBlockchain:
    # Prot NSB in uip
    def __init__(self, host_addr, nsb_addr, nsb_abi_addr, eth_db_addr, nsb_bytecode_addr=None):
        # , nsb_db_addr):
        self.handle = Contract(host_addr, nsb_addr, nsb_abi_addr, nsb_bytecode_addr)
        self.web3 = self.handle.web3
        self.address = self.handle.address
        self.pf_pool = {}
        print("test, so not linking to", eth_db_addr)
        # self.prover = Prover(eth_db_addr)
        pass

    def getQueueR(self):
        # return Queue[L,R) 's R
        return self.web3.eth.getStorageAt(self.address, SLOT_WAITING_QUEUE)

    def getQueueL(self):
        # return Queue[L,R) 's L
        return self.web3.eth.getStorageAt(self.address, SLOT_VOTEDPOINTER)

    def getQueueContent(self, idx):
        # return Queue[idx]
        return self.web3.eth.getStorageAt(self.address, LocationTransLator.queueloc(idx))

    def getMekleProofByHash(self, keccakhash):
        merkle_loc = bytestoint(LocationTransLator.merkleloc(keccakhash))
        merkleproof = MerkleProof(
            self.web3.eth.getStorageAt(self.address, catint32(merkle_loc)),
            self.web3.eth.getStorageAt(self.address, catint32(merkle_loc + 1)),
            self.web3.eth.getStorageAt(self.address, catint32(merkle_loc + 2)),
            self.web3.eth.getStorageAt(self.address, catint32(merkle_loc + 3))
        )
        print("    block_address", HexBytes(merkleproof.blockaddr).hex())
        print("    storageHash", HexBytes(merkleproof.storagehash).hex())
        print("    key", HexBytes(merkleproof.key).hex())
        print("    value", HexBytes(merkleproof.value).hex())
        return merkleproof

    def testgetMerkleProofByNumber(self, idx):
        a, h, k, v = self.handle.func('getMerkleProofByPointer', idx)
        print("idx: ", idx)
        print("    hash: ", HexBytes(self.handle.func('waitingVerifyProof', idx)).hex())
        print("    block_address", a)
        print("    storageHash", HexBytes(h).hex())
        print("    key", HexBytes(k).hex())
        print("    value", HexBytes(v).hex())

    def watchProofPool(self):
        queue_left, queue_right = bytestoint(self.getQueueL()), bytestoint(self.getQueueR())
        print(queue_left, queue_right)
        for idx in range(queue_left, queue_right):
            self.testgetMerkleProofByNumber(idx)
            print("idx: ", idx)
            keccakhash = self.getQueueContent(idx)
            print("    hash: ", HexBytes(keccakhash).hex())
            if bytestoint(keccakhash) == 0:
                continue
            if keccakhash not in self.pf_pool:
                self.pf_pool[keccakhash] = self.getMekleProofByHash(self.getQueueContent(idx))




    def work(self, work_time):
        pass
