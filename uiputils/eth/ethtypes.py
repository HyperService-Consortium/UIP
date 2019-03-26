
# python modules
from collections import namedtuple
from enum import Enum
import json
# import time

# uip modules
from uiputils.eth.tools.startservice import ServiceStart
from uiputils.cast import bytestoint, JsonRlpize
from uiputils.uiperror import (
    GenerationError,
    Mismatch,
    Missing
)

# eth modules
from .tools import (
    Prover,
    LocationTransLator,
    AbiEncoder,
    hex_match,
    hex_match_withprefix,
    FileLoad
)

# ethereum modules
from hexbytes import HexBytes
from eth_hash.auto import keccak
from eth_utils import is_address
from web3 import Web3

# config
from uiputils.config import eth_blockchain_info as blockchain_info
from uiputils.config import eth_unit_factor as unit_factor
from uiputils.config import eth_default_gasuse as default_gasuse

# constant
MOD6 = (1 << 6) - 1

MerkleProof = namedtuple('MerkleProof', 'blockaddr storagehash key value')


class StateType(Enum):
    unknown = 0
    init = 1
    inited = 2
    open = 3
    opened = 4
    closed = 5


class EthChainDNS:
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
        if chain_id in blockchain_info:
            if 'relay' in blockchain_info[chain_id]:
                return blockchain_info[chain_id]['relay']
            else:
                raise Missing('this chain has not relay-address' + chain_id)
        else:
            raise Missing('no such chainID: ' + chain_id)

    @staticmethod
    def gethost(chain_id):
        if chain_id in blockchain_info:
            return blockchain_info[chain_id]['host']
        else:
            raise Missing('no such chainID: ' + chain_id)


class EthTransaction:
    def __init__(self, transaction_type, *args, **kwargs):
        self.chain_host = ""
        self.chain_type = "Ethereum"
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

    def purejson(self):
        return json.dumps(self.__dict__, sort_keys=True)

    def pretjson(self):
        return json.dumps(self.__dict__, sort_keys=True, indent=4, separators=(', ', ': '))


class Contract:
    # return a contract that can transact with web3
    def __init__(self, web3_addr, contract_addr="", contract_abi=None, contract_bytecode=None):

        web3 = ServiceStart.startweb3(web3_addr)
        contract_abi = FileLoad.getabi(contract_abi)
        contract_bytecode = FileLoad.getbytecode(contract_bytecode)

        if contract_addr != "":
            self.handle = web3.eth.contract(Web3.toChecksumAddress(contract_addr), abi=contract_abi, bytecode=contract_bytecode)
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

    def funct(self, funcname, tx, *args, timeout=10):
        # transact a contract function
        tx_rec = self.handle.functions[funcname](*args).transact(tx)
        return self.web3.eth.waitForTransactionReceipt(HexBytes(tx_rec).hex(), timeout=timeout)

    def funcs(self):
        # return all functions in self.abi
        return self.handle.all_functions()


SLOT_WAITING_QUEUE = 0
SLOT_VOTEDPOINTER = 5
SLOT_MERKLEPROOFTREE = 6


class EthNetStatusBlockchain:
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
        merkleproof = MerkleProof(*self.handle.func('getMerkleProofByHash', keccakhash))
        print("    block_address", HexBytes(merkleproof.blockaddr).hex())
        print("    storageHash", HexBytes(merkleproof.storagehash).hex())
        print("    key", HexBytes(merkleproof.key).hex())
        print("    value", HexBytes(merkleproof.value).hex())
        return merkleproof

    def getMekleProofByPointer(self, idx):
        merkleproof = MerkleProof(*self.handle.func('getMerkleProofByPointer', idx))
        print("    block_address", HexBytes(merkleproof.blockaddr).hex())
        print("    storageHash", HexBytes(merkleproof.storagehash).hex())
        print("    key", HexBytes(merkleproof.key).hex())
        print("    value", HexBytes(merkleproof.value).hex())
        return merkleproof

    def watchProofPool(self):
        queue_left, queue_right = bytestoint(self.getQueueL()), bytestoint(self.getQueueR())
        print(queue_left, queue_right)
        for idx in range(queue_left, queue_right):
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

    def addAction(self, msg, sig):
        return self.handle.funct('addAction', self.tx, msg, sig)

    def getAction(self, keccakhash):
        return self.handle.func('getAction', keccakhash[2:])

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

    # def DiscreateTimer() override:

    # def CloseureWatching():

    # def CloseureClaim():


class EthInsuranceSmartContract:

    def __init__(self, host, isc_addr, isc_abi_dir, tx=None, isc_bytecode_dir=None):
        self.handle = Contract(host, Web3.toChecksumAddress(isc_addr), isc_abi_dir, isc_bytecode_dir)
        self.web3 = self.handle.web3
        self.address = self.handle.address
        if tx is not None:
            if 'gas' in tx:
                tx.pop('gas')
            if 'from' in tx:
                tx['from'] = Web3.toChecksumAddress(tx['from'])
        self.tx = tx
        # self.updateFunc = {
        #     'fr': partial(self.handle.funct, funcname='updateTxFr'),
        #     'to': partial(self.handle.funct, funcname='updateTxTo'),
        #     'seq': partial(self.handle.funct, funcname='updateTxSeq'),
        #     'amt': partial(self.handle.funct, funcname='updateTxAmt'),
        #     'rlped_data': partial(self.handle.funct, funcname='updateTxRlpedData')
        # }
        print(self.handle.funcs())

    def update_tx_info(
            self,
            idx,
            fr=None,
            to=None,
            seq=None,
            amt=None,
            meta=None,
            tx: dict = None,
            # spec: set = None,
            timeout=10
    ):
        if tx is None:
            tx = self.tx
        # if spec is None:
        if isinstance(meta, dict):
            meta = JsonRlpize.serialize(meta)
        elif not isinstance(meta, str) and not isinstance(meta, bytes):
            raise ValueError("unexpected meta-type" + str(type(meta)))
        return self.handle.funct(
            'updateTxInfo',
            tx,
            idx,
            Web3.toChecksumAddress(fr),
            Web3.toChecksumAddress(to),
            seq,
            amt,
            meta,
            timeout=timeout
        )
        # else:
        #     if 'fr' in spec:
        #         self.handle.funct('updateTxFr', tx, Web3.toChecksumAddress(fr), timeout=timeout)
        #     if 'to' in spec:
        #         self.handle.funct('updateTxTo', tx, Web3.toChecksumAddress(to), timeout=timeout)
        #     if 'seq' in spec:
        #         self.handle.funct('updateTxSeq', tx, seq, timeout=timeout)
        #     if 'amt' in spec:
        #         self.handle.funct('updateTxAmt', tx, amt, timeout=timeout)
        #     if 'rlped_meta' in spec:
        #         self.handle.funct('updateTxRlpedMeta', tx, rlped_meta, timeout=timeout)
        #     # return tuple((self.updateFunc[spec_type](kwargs) for spec_type in spec))

    def user_stake(self, tx):
        return self.handle.funct('stakeFund', tx)

    def user_ack(self, sig, tx=None):
        if tx is None:
            tx = self.tx
        return self.handle.funct('userAck', tx, sig)

    def user_refuse(self, tx=None):
        if tx is None:
            tx = self.tx
        return self.handle.funct('userRefuse', tx)

    def insurance_claim(self, atte, tid, state, nsb=None, result=None, tcg=None, tx=None):
        if tx is None:
            tx = self.tx
        print(atte, "is not verified")
        if state == StateType.opened:
            return self.handle.funct('ChangeStateOpened', tx, tid, tcg)
        elif state == StateType.closed:
            return self.handle.funct('ChangeStateClosed', tx, tid, tcg)
        elif state == StateType.open:
            return (
                self.handle.funct('ChangeState', tx, tid, state),
                self.handle.funct('ChangeResult', tx, nsb, tid, result)
            )
        else:
            return self.handle.funct('ChangeState', tx, tid, state)

    def stop_isc(self, tx=None):
        if tx is None:
            tx = self.tx
        return self.handle.funct('StopISC', tx)

    def settle_contract(self, tx=None):
        if tx is None:
            tx = self.tx
        return self.handle.funct('settleContract', tx)

    def return_funds(self, tx=None):
        if tx is None:
            tx = self.tx
        return self.handle.funct('returnFunds', tx)

    def is_owner(self, addr):
        return self.handle.func('isOwner', Web3.toChecksumAddress(addr))

    def get_meta_by_number(self, tid):
        return self.handle.func('getMetaByNumber', tid)

    def get_state(self, tid):
        return self.handle.func('getState', tid)

    def get_result(self, tid):
        return self.handle.func('getResult', tid)

    def get_transaction_info(self, tid):
        ret = self.handle.func('getTransactionInfo', tid)
        ret[4] = JsonRlpize.unserialize(ret[4])
        return ret
