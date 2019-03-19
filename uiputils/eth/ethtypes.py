
# python modules
from collections import namedtuple
# import time

# uip modules
from .loadfile import FileLoad
from .startservice import ServiceStart
from uiputils.cast import bytestoint, catint32
from .tools import (
    Prover,
    LocationTransLator,
    AbiEncoder,
    hex_match,
    hex_match_withprefix
)
from uiputils.uiperror import GenerationError, Mismatch, Missing

# ethereum modules
from hexbytes import HexBytes
from eth_hash.auto import keccak
from eth_utils import is_address
# from web3 import Web3

# config
from uiputils.config import eth_blockchain_info as blockchain_info
from uiputils.config import eth_unit_factor as unit_factor
from uiputils.config import eth_default_gasuse as default_gasuse

# constant
MOD6 = (1 << 6) - 1

MerkleProof = namedtuple('MerkleProof', 'blockaddr storagehash key value')


class ChainDNS:
    def __init__(self):
        pass

    @staticmethod
    def checkuser(chain_id, user_name):
        if is_address(user_name):
            return user_name
        if chain_id in blockchain_info:
            if user_name in blockchain_info[chain_id]['user']:
                return blockchain_info[chain_id]['user'][user_name]
            raise Missing('no user named ' + user_name + ' in ' + chain_id)
        else:
            raise Missing('no such chainID: ' + chain_id)

    @staticmethod
    def checkrelay(chain_id):
        if 'relay' in blockchain_info[chain_id]:
            return blockchain_info[chain_id]['relay']
        else:
            raise Missing('this chain has not relay-address' + chain_id)


class Transaction:
    def __init__(self, transaction_type, *args, **kwargs):
        self.chain_host = ""
        self.chain_type = "Ethereum"
        self.tx_info = {}
        getattr(self, transaction_type + 'Init')(*args, **kwargs)

    def transferInit(self, chain_id, src_addr, dst_addr, fund, fund_unit, gasuse=default_gasuse):
        self.chain_host = blockchain_info[chain_id]['host']
        self.tx_info = {
            'trans_type': 'transfer',
            'chain': chain_id + "@" + self.chain_host,
            'source': src_addr,
            'dst': dst_addr,
            'fund': hex(fund * unit_factor[fund_unit]),
            'unit': 'wei',
            'gas': gasuse
        }

    def deployInit(self, chain_id, code, gasuse=default_gasuse):
        self.chain_host = blockchain_info[chain_id]['host']
        self.tx_info = {
            'trans_type': 'deploy',
            'chain': chain_id + "@" + self.chain_host,
            'code': code,
            'gas': gasuse
        }

    def invokeInit(self, chain_id, invoker, contract_address,
                   function_name, function_parameters=None, function_parameters_description=None,
                   gasuse=default_gasuse):
        # if function parameters' description is not given, the function_parameters must be in format string
        self.chain_host = blockchain_info[chain_id]['host']
        self.tx_info = {
            'trans_type': 'invoke',
            'chain': chain_id + "@" + self.chain_host,
            'invoker': invoker,
            'address': contract_address,
            'func': function_name,
            'parameters': function_parameters,
            'gas': gasuse
        }

        # generate signature
        if len(function_name) == 8 and hex_match.match(function_name):
            setattr(self, 'signature', function_name)
        elif len(function_name) == 10 and hex_match_withprefix.match(function_name):
            setattr(self, 'signature', function_name)
        elif function_parameters_description:
            to_hash = bytes(
                (self.tx_info['func'] + '(' + ','.join(function_parameters_description) + ')').encode('utf-8')
            )
            signature = HexBytes(keccak(to_hash)[0:4]).hex()
            setattr(self, 'signature', signature)
        else:  # function_parameters_description is None
            raise GenerationError('function-signatrue can\'t be generated')

        setattr(self, 'parameters_description', function_parameters_description)

    def jsonize(self):
        return getattr(self, self.tx_info['trans_type'] + 'Jsonize')()

    '''
    {
        "from": "0x7019fa779024c0a0eac1d8475733eefe10a49f3b",
        "to": "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e",
        "gas": "0x40000",
        "value": "0x20"
    }
    '''

    def transferJsonize(self):
        return {
            "from": self.tx_info['source'],
            "to": self.tx_info['dst'],
            "gas": self.tx_info['gas'],
            "value": self.tx_info['fund']
        }

    def deployJsonize(self):
        return {
            "from": "0x7019fa779024c0a0eac1d8475733eefe10a49f3b",
            "data": self.tx_info['code'],
            "gas": self.tx_info['gas'],
        }

    def invokeJsonize(self):
        # self.tx_info['parameters']
        res = {
            "from": self.tx_info['invoker'],
            "to": self.tx_info['address'],
            "data": "",
            "gas": self.tx_info['gas']
        }
        if 'parameters' in self.tx_info:
            if hasattr(self, 'parameters_description'):
                parameters = AbiEncoder.encodes(self.tx_info['parameters'], getattr(self, 'parameters_description'))
                res['data'] = getattr(self, 'signature') + parameters
            else:  # without parameters_description
                if isinstance(self.tx_info['parameters'], str):
                    if not hex_match.match(self.tx_info['parameters']) and \
                            not hex_match_withprefix.match(self.tx_info['parameters']):
                        raise TypeError("bad encoded parameters given: not hexstring")
                    if self.tx_info['parameters'][1] == 'x':
                        if (len(self.tx_info['parameters']) - 2) & MOD6:
                            raise Mismatch("bad encoded parameters given: not multiple of 64(32 bytes)")
                        res['data'] = getattr(self, 'signature') + self.tx_info['parameters'][2:]
                    else:
                        if len(self.tx_info['parameters']) & MOD6:
                            raise Mismatch("bad encoded parameters given: not multiple of 64(32 bytes)")
                        res['data'] = getattr(self, 'signature') + self.tx_info['parameters']
                else:
                    raise Missing("no parameters_description to help encode the parameters")
        else:  # raw-function called
            res['data'] = self.tx_info['func']

        if 'value' in self.tx_info:
            res['value'] = self.tx_info['value']
        return res

    def __str__(self):
        return 'chain_host: ' + str(self.chain_host) +\
               '\ntransaction_intent: ' + str(self.tx_info)


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
    def __init__(self, owner_addr, host, nsb_addr, nsb_abi_dir, eth_db_dir="", gasuse=hex(400000),
                 nsb_bytecode_dir=None):
        # , nsb_db_addr):
        self.handle = Contract(host, nsb_addr, nsb_abi_dir, nsb_bytecode_dir)
        self.web3 = self.handle.web3
        self.address = self.handle.address
        self.pf_pool = {}
        self.tx = {
            "from": owner_addr,
            "gas": gasuse
        }
        print("test, so not linking to", eth_db_dir)
        self.prover = Prover(eth_db_dir)
        pass

    def setGas(self, gasuse):
        self.tx['gas'] = gasuse

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
            if keccakhash not in self.pf_pool and not self.ownerVoted(keccakhash):
                self.pf_pool[keccakhash] = self.getMekleProofByHash(self.getQueueContent(idx))

    def proveProofs(self):
        for keccakhash, merkleproof in self.pf_pool:
            is_valid_merkleproof = self.prover.verify(merkleproof)
            if is_valid_merkleproof is None:
                print("testmode? Because is_valid_merkleproof is None")
            else:
                self.handle.funct('voteProofByHash', keccakhash, is_valid_merkleproof)
                self.pf_pool.pop(keccakhash)

    def addAction(self, signature):
        return self.handle.funct('addAction', self.tx, signature)

    def getAction(self, keccakhash):
        print("getAction is not finished")
        # print(self.handle.func('getAction', keccakhash[2:]))
        return self.web3.eth.getStorageAt(self.address, LocationTransLator.actionloc(HexBytes(keccakhash)))

    def validMerkleProoforNot(self, keccakhash):
        return self.handle.func('validMerkleProoforNot', keccakhash) == 1

    def getValidMerkleProof(self, keccakhash):
        return self.handle.func('getValidMerkleProof', keccakhash)

    def blockHeigth(self):
        pass

    def ownerVoted(self, keccakhash):
        pass

    def work(self, work_time):
        pass

    def exec(self, contract):
        pass

    # def DiscreateTimer() override:

    # def CloseureWatching():

    # def CloseureClaim():
