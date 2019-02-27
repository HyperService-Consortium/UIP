#!/usr/bin/python

# from ctypes import *
from hexbytes import HexBytes
from eth_hash.auto import keccak
import json, requests, time
import rlp, eth_rlp
# import plyvel
# ethdb = cdll.LoadLibrary("./goleveldb.dll")


BLOCKCHAIN_A = "private_A"
BLOCKCHAIN_B = "private_B"
BLOCKCHAIN_C = "Rinkeby"
BLOCKCHAIN_D = "Popsten"

NETWORK_SETUP = {
        BLOCKCHAIN_A: "http://127.0.0.1:8545",
        BLOCKCHAIN_B: "http://127.0.0.1:8599",
        BLOCKCHAIN_C: "http://127.0.0.1:8545",
        BLOCKCHAIN_D: "http://127.0.0.1:8545"
        }

# Configuration.
# "YourPassWord`"
UNLOCK_PWD = "123456"
HTTP_HEADERS = {'Content-Type': 'application/json'}
ACCOUNT_UNLOCK_PERIOD = 3000
ETHDB_PATH = "D:\\Go Ethereum\\data\\geth\\chaindata"


class BlockchainNetwork:
    def __init__(self, identifer="", rpc_port=0, data_dir="", listen_port=0, host="", public=False):
        self.identifer = identifer
        self.rpc_port = rpc_port
        self.data_dir = data_dir
        self.listen_port = listen_port
        self.host = host
        self.public = public


class SmartContract:
    # The abstracted structure of a SmartContract.
    def __init__(self, bytecode="", domain="", name="", gas=hex(0), value=hex(0)):
        self.bytecode = bytecode
        self.domain = domain
        self.name = name
        self.gas = gas
        self.value = value


# The Merkle Proof for a Blockchain state.
class StateProof:
    def __init__(self, value, block, proof):
        self.value = value
        self.block = block
        self.proof = proof

    def __str__(self):
        return "value: %s;block: %s;proof: %s;" % (self.value, self.block, self.proof);

    def TransIntoHex(self, nodelist):
        decodelist = []
        for node in nodelist:
            if isinstance(node, list):
                decodelist.append(self.TransIntoHex(node))
            elif isinstance(node, bytes):
                decodelist.append(HexBytes(node).hex())
            else:
                raise TypeError("node must be str or list, But %s." % node.__name__)
        return decodelist

    def decode(self, varlist):
        return self.TransIntoHex(rlp.decode(HexBytes(varlist)))

class JsonRPC:
    def __init__(self):
        pass

    @staticmethod
    def ethCoinbase():
        # return the method of eth_coinbase
        return {
                "jsonrpc": "2.0",
                "method": "eth_coinbase",
                "params": [],
                "id": 64
                }

    @staticmethod
    def ethGetProof(addr, key=[], tag="latest"):
        # return the method of eth_getProof
        # addr: the contract's account address
        # key: Array of the storageKey needed to proof
        # tag: block id(known as the default block parameter)
        # can be "latest","earliest","pending", or the interger block number
        return {
                "jsonrpc": "2.0",
                "method": "eth_getProof",
                "params": [addr, key, tag],
                "id": 1
                }

    @staticmethod
    def ethGetStorageAt(sto, pos, tag="latest"):
        # return the value stored at the pos
        # sto: the deployed contract's account address
        # pos: a sha3-hashed value of (position+1)
        # tag: block id(known as the default block parameter)
        # can be "latest","earliest","pending", or the interger block number
        return {
                "jsonrpc":"2.0",
                "method": "eth_getStorageAt",
                "params": [sto, pos, tag],
                "id": 1
                }

    @staticmethod
    def web3Sha3(tostr):
        # return the value of keccak256(tostr)
        return {
                "jsonrpc":"2.0",
                "method": "web3_sha3",
                "params": [tostr],
                "id": 64
                }

    @staticmethod
    def ethMining():
        # return if the miner is mining
        return {
                "jsonrpc": "2.0",
                "method": "eth_mining",
                "params": [],
                "id": 71
                }

    @staticmethod
    def ethAccounts():
        # return the accounts on the current service
        return {
                "jsonrpc": "2.0",
                "method": "eth_accounts",
                "params": [],
                "id": 1
                }

    @staticmethod
    def ethBlockNumber():
        # return the number of most recent block
        return {
                "jsonrpc": "2.0",
                "method": "eth_blockNumber",
                "params": [],
                "id": 1
                }

    @staticmethod
    def ethGetBalance(addr, tag="latest"):
        # returns the balance of the account of given address
        # addr: address to check for balance
        # tag: block id(known as the default block parameter)
        # can be "latest","earliest","pending", or the interger block number
        return {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [addr, tag],
                "id": 1
                }

    @staticmethod
    def ethGetCode(addr, tag="latest"):
        # returns code at a given address
        # addr: address to check for balance
        # tag: block id(known as the default block parameter)
        # can be "latest","earliest","pending", or the interger block number
        return {
                "jsonrpc": "2.0",
                "method": "eth_getCode",
                "params": [addr, tag],
                "id": 1
                }

    @staticmethod
    def ethSign(addr, data):
        # return the value of sign(keccak256("\x19Ethereum Signed Message:\n" + len(message) + message))
        # addr: address to sign with
        # data: datastr to sign
        return {
                "jsonrpc": "2.0",
                "method": "eth_sign",
                "params": [addr, data],
                "id": 1
                }

    @staticmethod
    def ethSendTransaction(obj):
        # create a transaction and return the corresponding transaction hash
        # a obj(json) describe the transaction
        # obj has attributes:
        #   from: address, to: address,
        #   gas: hex string, gasprice: hex string, value: hex string, data: hex string
        return {
                "jsonrpc": "2.0",
                "method": "eth_sendTransaction",
                "params": [obj],
                "id": 1
                }

    @staticmethod
    def ethGetBlockByHash(blockhash, fullinfo):
        # returns information about a block by hash
        # blockhash: hash of a block
        # fullinfo: return the block's full information or not
        return {
                "jsonrpc": "2.0",
                "method": "eth_getBlockByHash",
                "params": [blockhash, fullinfo],
                "id": 1
                }

    @staticmethod
    def ethGetBlockByNumber(tag, fullinfo):
        # returns information about a block by Number
        # tag: block id(known as the default block parameter)
        # can be "latest","earliest","pending", or the interger block number
        # fullinfo: return the block's full information or not
        return {
                "jsonrpc": "2.0",
                "method": "eth_getBlockByNumber",
                "params": [tag, fullinfo],
                "id": 1
                }

    @staticmethod
    def ethGetTransactionReceipt(transactionhash):
        # returns the receipt of a transaction by transaction hash
        # transactionhash: hash of a transaction
        return {
                "jsonrpc": "2.0",
                "method": "eth_getTransactionReceipt",
                "params": [transactionhash],
                "id": 1
                }

# class EthDB(leveldb.LevelDB):
    # the child class of LevelDB

    # Get(key, verify_checksums=False, fill_cache=True): get value, raises KeyError if key not found
    # key: the query key

    # Put(key, value, sync=False): put key / value pair
    # key: the key
    # value: the value

    # Delete(key, sync=False): delete key / value pair, raises no error if key not found
    # key: the key

    # Write(write_batch, sync=False): apply multiple put / delete operations atomatically
    # write_batch: the WriteBatch object holding the operations

    # RangeIter(key_from = None, key_to = None, include_value = True,
    #           verify_checksums = False, fill_cache = True): return iterator
    # key_from: if not None: defines lower bound (inclusive) for iterator
    # key_to:   if not None: defined upper bound (inclusive) for iterator
    # include_value: if True, iterator returns key/value 2-tuples, otherwise, just keys

    # GetStats(): get a string of runtime information
    # Methods defined here:

    # CompactRange(...)
    # Compact keys in the range

    # CreateSnapshot(...)
    # create a new snapshot from current DB state

    # __init__(self, /, *args, **kwargs)
    # Initialize self.  See help(type(self)) for accurate signature.

    # def __init__(self, var):
    #     # var can be string of path or DB
    #     if isinstance(var, str):
    #         # create_if_missing=True
    #         # paranoid_checks=False
    #         leveldb.LevelDB.__init__(var, error_if_exists=True)
    #     elif isinstance(var, leveldb.LevelDB):
    #         pass
    #     else:
    #         raise TypeError("need path or LevelDB, But gets %s." % var.__name__)

    # __new__(*args, **kwargs) from builtins.type
    # Create and return a new object.  See help(type) for accurate signature.


# ethdb = plyvel.DB(ETHDB_PATH)#  error_if_exists=True)

jsonLoad = JsonRPC()

class HyperService:
    def __init__(self, domains):
        self.domain_handles = {}
        self.EstablishBNVisibility(domains)
        self.contracts = {}

    def DispatchRpcToDomain(self, url, data):
        # dispatch RPC to domains(Blockchians)
        response = requests.post(
            url,
            headers=HTTP_HEADERS,
            data=json.dumps(data))
        if response.status_code != 200 or 'error' in response.json():
            print(json.dumps(data))
            raise Exception(response.json())

        return response.json()

    def EstablishBNVisibility(self, domains):
        for domain in domains:
            coinbase = {
                        "jsonrpc": "2.0",
                        "method": "eth_coinbase",
                        "params": [],
                        "id": 64
                        }
            url = NETWORK_SETUP[domain]
            response = self.DispatchRpcToDomain(url, coinbase)
            self.domain_handles[domain] = response['result']

            # Unlock account for furture use.
            unlock = {
                    "jsonrpc": "2.0", 
                    "method": "personal_unlockAccount",
                    "params":[self.domain_handles[domain],
                        UNLOCK_PWD, ACCOUNT_UNLOCK_PERIOD],
                    "id": 64
                    }
            response = self.DispatchRpcToDomain(url, unlock)

    def DeployContract(self, contract):
        if contract.domain not in self.domain_handles:
            raise Exception("Unsupported domain: " + contract.domain)

        handle = self.domain_handles[contract.domain]
        deploy = {
                "jsonrpc": "2.0",
                "method": "eth_sendTransaction",
                "params": [{
                    "from": handle,
                    "data": contract.bytecode,
                    "gas": contract.gas,
		            "value": contract.value,
                    }],
                "id": 64
                }
        url = NETWORK_SETUP[contract.domain]
        response = self.DispatchRpcToDomain(url, deploy)
        tx_hash = response['result']
        contract_addr = self.RetrieveContractAddress(url, tx_hash)
        print ("Contract is deployed at address: " + contract_addr)
        self.contracts[contract_addr] = contract

    def RetrieveContractAddress(self, url, tx_hash):
        get_tx = {
                "jsonrpc":"2.0", 
                "method":"eth_getTransactionReceipt",
                "params": [tx_hash],
                "id":64
                }

        while True:
            response = self.DispatchRpcToDomain(url, get_tx)
            if response['result'] is None:
                print ("Contract is deploying, please stand by")
                time.sleep(2)
                continue

            block_number = response['result']['blockNumber']
            contract_addr = response['result']['contractAddress']
            get_code = {
                    "jsonrpc": "2.0",
                    "method": "eth_getCode",
                    "params": [contract_addr, block_number],
                    "id": 64
                    }
            code_resp = self.DispatchRpcToDomain(url, get_code)
            if code_resp['result'] is '0x':
                raise IndexError("Contract deployment failed")
            return contract_addr


    def GetAuthenticatedPriceFromBroker(self):
        for index, (addr, contract) in enumerate(self.contracts.items()):
            # print(contract)
            if contract.name is 'BrokerContract':
                return self.GetContractState(addr, 0)

    def GetContractState(self, contract, index, block="latest"):
        if contract not in self.contracts:
            raise Exception("No contract is found " + contract)

        
        domain = self.contracts[contract].domain
        url = NETWORK_SETUP[domain]
        get_state = {
            "jsonrpc": "2.0", 
            "method": "eth_getStorageAt",
            "params": [contract, hex(index), block],
            "id": 64
        }
        value_response = self.DispatchRpcToDomain(url, get_state)
	
        get_proof = {
            "jsonrpc": "2.0", 
            "method": "eth_getProof",
            "params": [contract, [hex(index)], block],
            "id": 64
        }
        proof_response = self.DispatchRpcToDomain(url, get_proof)
        state_proof = proof_response['result']['storageProof']
        return StateProof(value_response['result'], block, state_proof)



def funcTrans(nodelist):
    decodelist = []
    for node in nodelist:
        if isinstance(node, list):
            decodelist.append(funcTrans(node))
        elif isinstance(node, bytes):
            decodelist.append(HexBytes(node).hex())
        else:
            raise TypeError("node must be str or list, But %s." % node.__name__)
    return decodelist

if __name__ == '__main__':

    supported_chains = [BLOCKCHAIN_A]#, BLOCKCHAIN_B]
    hyperservice = HyperService(supported_chains)


    # Deploy the Broker and Option contract.
    # with open('broker_bytecode', 'r') as f:
    #     BrokerBytecode = f.read()
    #     broker_contract = SmartContract(
    #         BrokerBytecode[:-1], BLOCKCHAIN_A,
    #         "BrokerContract", hex(2000000))
    #     hyperservice.DeployContract(broker_contract)
    #     queryProof = hyperservice.GetAuthenticatedPriceFromBroker()
    #     print(queryProof)

    # with open('option_bytecode', 'r') as f:
    #     OptionBytecode = f.read()
    #     option_contract = SmartContract(
    #         OptionBytecode[:-1], BLOCKCHAIN_A,
    #         "OptionContract", hex(200000), "0x8ac7230489e80000")
    #     hyperservice.DeployContract(option_contract)
    with open('NSB_bytecode', 'r') as f:
        NSBBytecode = f.read()
        NSB_contract = SmartContract(
            NSBBytecode[:-1], BLOCKCHAIN_A,
            "OptionContract", hex(5500000), hex(500000))
        hyperservice.DeployContract(NSB_contract)

    # print(hyperservice.contracts)
