
# python modules
import json
import requests

from uiputils.config import HTTP_HEADER

class JsonRPC(object):
    # JSON-RPC methods
    def __init__(self):
        pass

    @staticmethod
    def eth_accounts():
        # return the method of eth_accounts
        # return the accounts on the current service
        return {
            "jsonrpc": "2.0",
            "method": "eth_accounts",
            "params": [],
            "id": 1
        }

    @staticmethod
    def eth_block_number():
        # return the method of eth_blockNumber
        # return the number of most recent block
        return {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }

    @staticmethod
    def eth_call(obj, tag="latest"):
        # return the method of eth_call
        # call a contract-function without on-chain operation
        # obj: transaction object
        # tag: block id(known as the default block parameter)
        # can be "latest","earliest","pending", or the interger block number
        return {
            "jsonrpc": "2.0",
            "method": "eth_call",
            "params": [obj, tag],
            "id": 1
        }

    @staticmethod
    def eth_coinbase():
        # return the method of eth_coinbase
        return {
            "jsonrpc": "2.0",
            "method": "eth_coinbase",
            "params": [],
            "id": 64
        }

    @staticmethod
    def eth_estimate_gas():
        # return the method of eth_estimateGas
        # Generates and returns an estimate of how much gas is necessary to allow the transaction to complete. The tran-
        # saction will not be added to the blockchain. Note that the estimate may be significantly more than the amount
        # of gas actually used by the transaction, for a variety of reasons including EVM mechanics and node performanc-
        # e.
        return {
            "jsonrpc": "2.0",
            "method": "eth_estimateGas",
            "params": [],
            "id": 1
        }

    @staticmethod
    def eth_gas_price():
        # return the method of eth_gasPrice
        # returns the current price per gas in wei.
        return {
            "jsonrpc": "2.0",
            "method": "eth_gasPrice",
            "params": [],
            "id": 73
        }

    @staticmethod
    def eth_get_balance(addr, tag="latest"):
        # return the method of eth_getBalance
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
    def eth_get_block_by_hash(blockhash, fullinfo):
        # return the method of eth_getBlockByHash
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
    def eth_get_block_by_number(tag, fullinfo):
        # return the method of eth_getBlockByNumber
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
    def eth_get_code(addr, tag="latest"):
        # return the method of eth_getCode
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
    def eth_get_proof(addr, key=None, tag="latest"):
        # return the method of eth_getProof
        # addr: the contract's account address
        # key: Array of the storageKey needed to proof
        # tag: block id(known as the default block parameter)
        # can be "latest","earliest","pending", or the interger block number
        if key is None:
            key = []
        return {
            "jsonrpc": "2.0",
            "method": "eth_getProof",
            "params": [addr, key, tag],
            "id": 1
        }

    @staticmethod
    def eth_get_storage_at(sto, pos, tag="latest"):
        # return the method of eth_getStorageAt
        # return the value stored at the pos
        # sto: the deployed contract's account address
        # pos: a sha3-hashed value of (position+1)
        # tag: block id(known as the default block parameter)
        # can be "latest","earliest","pending", or the interger block number
        return {
            "jsonrpc": "2.0",
            "method": "eth_getStorageAt",
            "params": [sto, pos, tag],
            "id": 1
        }

    @staticmethod
    def eth_get_transaction_by_hash(transactionhash):
        # return the method of eth_getTransactionByHash
        # returns the information about a transaction requested by transaction hash.
        # transactionhash: hash of a transaction
        return {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByHash",
            "params": [transactionhash],
            "id": 1
        }

    @staticmethod
    def eth_get_transaction_by_block_hash_and_index(blockhash, idx):
        # return the method of eth_getTransactionByBlockHashAndIndex
        # returns information about a transaction by block hash and transaction index position.
        # blockhash: hash of a block.
        # idx: integer of the transaction index position.
        return {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByBlockHashAndIndex",
            "params": [blockhash, idx],
            "id": 1
        }

    @staticmethod
    def eth_get_transaction_by_block_number_and_index(tag, idx):
        # return the method of eth_getTransactionByBlockNumberAndIndex
        # returns information about a transaction by block number and transaction index position.
        # tag: block id(known as the default block parameter)
        # can be "latest","earliest","pending", or the interger block number
        # idx: integer of the transaction index position.
        return {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByBlockNumberAndIndex",
            "params": [tag, idx],
            "id": 1
        }

    @staticmethod
    def eth_get_transaction_receipt(transactionhash):
        # return the method of eth_getTransactionReceipt
        # returns the receipt of a transaction by transaction hash
        # transactionhash: hash of a transaction
        return {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionReceipt",
            "params": [transactionhash],
            "id": 1
        }

    @staticmethod
    def eth_mining():
        # return the method of eth_mining
        # return if the miner is mining
        return {
            "jsonrpc": "2.0",
            "method": "eth_mining",
            "params": [],
            "id": 71
        }

    @staticmethod
    def eth_syncing():
        # return the method of eth_syncing
        # return an object with data about the sync status or false
        # startingBlock: The block at which the import started (will only be reset, after the sync reached his head)
        # currentBlock: The current block, same as eth_blockNumber
        # highestBlock: The estimated highest block
        return {
            "jsonrpc": "2.0",
            "method": "eth_syncing",
            "params": [],
            "id": 1
        }

    @staticmethod
    def eth_send_raw_transaction(data):
        # return the method of eth_sendRawTransaction
        # create a transaction and return the corresponding transaction hash
        # data: The signed transaction data.
        return {
            "jsonrpc": "2.0",
            "method": "eth_sendRawTransaction",
            "params": [data],
            "id": 1
        }

    @staticmethod
    def eth_send_transaction(obj):
        # return the method of eth_sendTransaction
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
    def eth_sign(addr, data):
        # return the method of eth_sign
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
    def net_version():
        # return the method of net_version
        # return the current network id.
        # "1" : Ethereum Mainnet
        # "2" : Morden Testnet (deprecated)
        # "3" : Ropsten Testnet
        # "4" : Rinkeby Testnet
        # "42": Kovan Testnet
        return {
            "jsonrpc": "2.0",
            "method": "net_version",
            "params": [],
            "id": 67
        }

    @staticmethod
    def net_listening():
        # returns true if client is actively listening for network connections.
        return {
            "jsonrpc": "2.0",
            "method": "net_listening",
            "params": [],
            "id": 67
        }

    @staticmethod
    def net_peer_count():
        # returns number of peers currently connected to the client.
        return {
            "jsonrpc": "2.0",
            "method": "net_peerCount",
            "params": [],
            "id": 74
        }

    @staticmethod
    def personal_unlock_account(addr, passphrase, duration=600):
        # unlock an account of ethereum
        # addr: the account's address
        # passphrase: (! the account's password !)
        # duration: unlock duration
        return {
            "jsonrpc": "2.0",
            "method": "personal_unlockAccount",
            "params": [addr, passphrase, duration],
            "id": 64
        }

    @staticmethod
    def web3_sha3(tostr):
        # return the value of keccak256(tostr)
        return {
            "jsonrpc": "2.0",
            "method": "web3_sha3",
            "params": [tostr],
            "id": 64
        }

    @staticmethod
    def web3_client_version():
        # return the current client version.
        return {
            "jsonrpc": "2.0",
            "method": "web3_clientVersion",
            "params": [],
            "id": 67
        }

    @staticmethod
    def send(dat, hed=HTTP_HEADER, rpc_host='http://127.0.0.1:8545'):
        response = requests.post(rpc_host, headers=hed, data=json.dumps(dat))
        if response.status_code != 200 or 'error' in response.json():
            print(json.dumps(dat))
            raise Exception(response.json())
        return response.json()


if __name__ == '__main__':
    RPC_HOST = 'http://127.0.0.1:8545'

    '''Sample One
    transaction = {
        "from": "0x7019fa779024c0a0eac1d8475733eefe10a49f3b",
        "to": "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e",
        "gas": "0x40000",
        "value": "0x20"
    }
    packet_transaction = JsonRPC.ethSendTransaction(transaction)
    tx_response = JsonRPC.send(packet_transaction, HTTP_HEADER, RPC_HOST)
    tx_hash = tx_response['result']
    query = JsonRPC.ethGetTransactionReceipt(tx_hash)

    import time
    while True:
        time.sleep(1)
        tx_result = JsonRPC.send(query, HTTP_HEADER, RPC_HOST)
        if tx_result['result'] is None:
            continue
        else:
            print(tx_result['result'])
            break
    '''
    '''Sample Two
    query = JsonRPC.ethGetBlockByHash("0xfcaa6554604880ef255d502c542d8d66adb3358369cd3c81f3862615dd8d02a5", False)
    print(JsonRPC.send(query, HTTP_HEADER, RPC_HOST))
    '''
