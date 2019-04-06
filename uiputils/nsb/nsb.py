
# ethereum modules
from hexbytes import HexBytes
from web3 import Web3

# uip modules
from uiputils.uiptools.cast import bytestoint
from uiputils.uiptypes import MerkleProof
from uiputils.contract.wrapped_contract_function import(
    ContractFunctionWithoutCheck,
    ContractFunctionClient
)

# eth modules
from uiputils.contract.eth_contract import EthContract
from uiputils.ethtools import(
    AbiEncoder,
    AbiDecoder,
    Prover,
    JsonRPC,
    LocationTransLator
)

# constant
SLOT_WAITING_QUEUE = 0
SLOT_VOTEDPOINTER = 5
SLOT_MERKLEPROOFTREE = 6


class EthLightNetStatusBlockChain:
    Function_Sign = {
        'add_transaction_proposal': "0x3aadafba",
        'is_active_isc': "0x5640ee94"
    }

    def __init__(
        self,
        owner_addr,
        host,
        nsb_addr,
        tx=None,
        timeout=25
    ):
        self.host = host
        self.address = nsb_addr
        self.owner = Web3.toChecksumAddress(owner_addr)
        self.timeout = timeout
        if tx is None:
            self.tx = {
                "from": self.owner,
                "gas": hex(4000000),
                "data": None,
                "to": nsb_addr
            }
        else:
            self.tx = tx.copy()
            if 'from' in self.tx:
                self.tx['from'] = Web3.toChecksumAddress(self.tx['from'])
            self.tx["to"] = nsb_addr

    def add_transaction_proposal(self, isc_addr, tx_count, timeout=25):
        return ContractFunctionClient(
            function_transact=ContractFunctionWithoutCheck.transact(
                self.host,
                EthLightNetStatusBlockChain.Function_Sign['add_transaction_proposal'],
                [isc_addr, tx_count],
                ['address', 'uint'],
            ),
            wait_catch=ContractFunctionWithoutCheck.wait(self.host),
            tx=self.tx,
            timeout=timeout
        )

    def is_active_isc(self, isc_addr, ):
        return ContractFunctionWithoutCheck.call(
            self.host,
            EthLightNetStatusBlockChain.Function_Sign['is_active_isc'],
            [isc_addr],
            ['address'],
        )(self.tx)[-1] == '1'


class EthNetStatusBlockchain:
    # Prot NSB in uip

    # self settings

    def __init__(
            self,
            owner_addr,
            host,
            nsb_addr,
            nsb_abi_dir,
            eth_db_dir="",
            tx=None,
            nsb_bytecode_dir=None,
            timeout=25
    ):
        # , nsb_db_addr):

        self.handle = EthContract(host, nsb_addr, nsb_abi_dir, nsb_bytecode_dir, timeout=timeout)
        self.web3 = self.handle.web3
        self.address = self.handle.address
        self.owner = Web3.toChecksumAddress(owner_addr)
        self.pf_pool = {}
        if tx is None:
            self.tx = {
                "from": self.owner,
                "gas": hex(400000)
            }
        else:
            self.tx = tx.copy()
            if 'from' in self.tx:
                self.tx['from'] = Web3.toChecksumAddress(self.tx['from'])
        print("test, so not linking to", eth_db_dir)
        self.prover = Prover(eth_db_dir)
        pass

    def set_gas(self, gasuse):
        self.tx['gas'] = gasuse

    def set_timeout(self, timeout):
        self.handle.timeout = timeout

    #################

    # owner system

    def add_owner(self, addr):
        return self.handle.funct('addOwner', self.tx, Web3.toChecksumAddress(addr))

    def is_owner(self, addr):
        return self.handle.func('isOwner', Web3.toChecksumAddress(addr))

    def remove_owner(self, addr):
        return self.handle.funct('removeOwner', self.tx, Web3.toChecksumAddress(addr))

    def get_owner(self):
        return self.handle.func('getOwner')

    def get_queue_r(self):
        # return Queue[L,R) 's R
        return AbiDecoder.decode('uint', self.web3.eth.getStorageAt(self.address, SLOT_WAITING_QUEUE))

    def get_queue_l(self):
        # return Queue[L,R) 's L
        return AbiDecoder.decode('uint', self.web3.eth.getStorageAt(self.address, SLOT_VOTEDPOINTER))

    def get_queue_content(self, idx):
        # return Queue[idx]
        return self.web3.eth.getStorageAt(self.address, LocationTransLator.queueloc(idx))

    def get_merkle_proof_by_hash(self, keccakhash):
        merkleproof = MerkleProof(*self.handle.func('getMerkleProofByHash', keccakhash))
        print("    block_address", HexBytes(merkleproof.blockaddr).hex())
        print("    storageHash", HexBytes(merkleproof.storagehash).hex())
        print("    key", HexBytes(merkleproof.key).hex())
        print("    value", HexBytes(merkleproof.value).hex())
        return merkleproof

    def get_merkle_proof_by_pointer(self, idx):
        merkleproof = MerkleProof(*self.handle.func('getMerkleProofByPointer', idx))
        print("    block_address", HexBytes(merkleproof.blockaddr).hex())
        print("    storageHash", HexBytes(merkleproof.storagehash).hex())
        print("    key", HexBytes(merkleproof.key).hex())
        print("    value", HexBytes(merkleproof.value).hex())
        return merkleproof

    def watch_proof_pool(self):
        queue_left, queue_right = bytestoint(self.get_queue_l()), bytestoint(self.get_queue_r())
        print(queue_left, queue_right)
        for idx in range(queue_left, queue_right):
            print("idx: ", idx)
            keccakhash = self.get_queue_content(idx)
            print("    hash: ", HexBytes(keccakhash).hex())
            if bytestoint(keccakhash) == 0:
                continue
            if keccakhash not in self.pf_pool and not self.owner_voted(keccakhash):
                self.pf_pool[keccakhash] = self.get_merkle_proof_by_hash(self.get_queue_content(idx))

    def prove_proofs(self):
        for keccakhash, merkleproof in self.pf_pool:
            is_valid_merkleproof = self.prover.verify(merkleproof)
            if is_valid_merkleproof is None:
                print("testmode? Because is_valid_merkleproof is None")
            else:
                self.handle.funct('voteProofByHash', keccakhash, is_valid_merkleproof)
                self.pf_pool.pop(keccakhash)

    def add_action(self, msg, sig):
        return self.handle.funct('addAction', self.tx, msg, sig)

    def get_action(self, keccakhash):
        return self.handle.func('getAction', keccakhash[2:])

    def valid_merkle_proofor_not(self, keccakhash):
        return self.handle.func('validMerkleProoforNot', keccakhash) == 1

    def get_valid_merkle_proof(self, keccakhash):
        return self.handle.func('getValidMerkleProof', keccakhash)

    def block_heigth(self):
        pass

    def owner_voted(self, keccakhash):
        pass

    def work(self, work_time):
        pass

    # transaction system

    def add_transaction_proposal(self, addr, tx_count, gasuse=None):
        return self.handle.lazyfunct('addTransactionProposal', self.tx, Web3.toChecksumAddress(addr), tx_count, gasuse=gasuse)

    def is_active_isc(self, addr):
        return self.handle.func('activeISC', Web3.toChecksumAddress(addr))
        # return self.web3.eth.getStorageAt(self.address, MapLoc.cast(17, addr))

    # def DiscreateTimer() override:

    # def CloseureWatching():

    # def CloseureClaim():


class NetworkStatusBlockChain:
    def __init__(self, nsb_type="ethereum", *args, **kwargs):
        if nsb_type == "ethereum":
            self.handle = EthNetStatusBlockchain(*args, **kwargs)
        else:
            self.handle = None
            raise TypeError("other NSB type not implemented")
