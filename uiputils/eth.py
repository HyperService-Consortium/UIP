

'eth methods'

import json
from ctypes import *
from uiputils.gotypes import GoString, GoInt32, GoStringSlice

PROVER_PATH = "./uiputils/include/verifyproof.dll"
ENC = "utf-8"


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


class FileLoad(object):
    # simply load files
    def __int__(self):
        pass

    @staticmethod
    def getabi(contract_abi):
        if isinstance(contract_abi, str):
            with open(contract_abi, "r") as abifile:
                return json.load(abifile)
        else:
            return contract_abi

    @staticmethod
    def getbytecode(contract_bytecode):
        if isinstance(contract_bytecode, str):
            with open(contract_bytecode, "rb") as bytecodefile:
                return bytecodefile.read()
        else:
            return contract_bytecode


class JsonRPC:
    # JSON-RPC methods
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


dbptr = c_void_p

funcs = CDLL(PROVER_PATH)

funcs.openDB.restype = dbptr
funcs.openDB.argtype = GoString

funcs.closeDB.argtype = dbptr

funcs.VerifyProof.restype = GoInt32
funcs.VerifyProof.argtypes = (dbptr, GoString, GoString, GoString, GoStringSlice, GoInt32)


class Prover:
    def __init__(self, path):
        self.ethdb = funcs.openDB(bytes(path.encode(ENC)))

    def close(self):
        funcs.closeDB(self.ethdb)

    def verify(self, StorageHash, key, val, StoragePath):
        strs = [c_char_p(bytes(path.encode(ENC))) for path in StoragePath]
        lenx = len(StoragePath)
        charparray = c_char_p * lenx
        charlist = charparray(*strs)
        funcs.VerifyProof(self.ethdb, StorageHash, key, val, cast(charlist, POINTER(GoString)), lenx)