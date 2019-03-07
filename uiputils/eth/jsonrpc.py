
class JsonRPC(object):
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
