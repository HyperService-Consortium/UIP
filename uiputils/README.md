# uiputils.eth

## JSON-RPC

Start with:

```python
from uiputils.eth import JsonRPC
```

Read the document [ethereum wiki JSON-RPC][JSON-RPC] to know all the methods of JSON-RPC.

Sample:

```python
>>> JsonRPC.ethCoinbase()
{'jsonrpc': '2.0', 'method': 'eth_coinbase', 'params': [], 'id': 64}
>>> JsonRPC.ethGetProof("0xe1300d8ea0909faa764c316436ad0ece571f62b2", ["0x0"])
{'jsonrpc': '2.0', 'method': 'eth_getProof', 'params': ['0xe1300d8ea0909faa764c316436ad0ece571f62b2', ['0x0'], 'latest'], 'id': 1}
```

|                    class JSON-RPC                    |       eth JSON-RPC        |
| :--------------------------------------------------: | :-----------------------: |
|                    ethCoinbase()                     |       eth_coinbase        |
|      ethGetProof(address addr, list keys, tag)       |       eth_getProof        |
|    ethGetStorageAt(address sto, uint256 pos, tag)    |     eth_getStorageAt      |
|           web3Sha3(string to_hash_string)            |         web3_sha3         |
|                     ethMining()                      |        eth_mining         |
|                    ethAccounts()                     |       eth_accounts        |
|                   ethBlockNumber()                   |      eth_blocknumber      |
|               ethGetCode(address addr)               |        eth_getCode        |
|          ethSign(address addr, string data)          |         eth_sign          |
|     ethSendTransaction(json_object Transaction)      |    eth_sendTransaction    |
| ethGetBlockByHash(uint256 blockhash, bool fullinfo)  |    eth_getBlockByHash     |
|       ethGetBlockByNumber(tag, bool fullinfo)        |   eth_getBlockByNumber    |
|      ethGetTransactionReceipt(transactionhash)       | eth_getTransactionReceipt |
| send(url blockchain_address, headers hed, json data) |             /             |

##### function ethCoinbase()

```python
>>> JsonRPC.ethCoinbase()
{'jsonrpc': '2.0', 'method': 'eth_coinbase', 'params': [], 'id': 64}
```

##### function ethGetProof(address addr, list keys, tag)

```python
>>> JsonRPC.ethGetProof("0x85854fe3853b7A51576bFd78564Ec1993f8820d1",["0x01", "0x00"], "latest")
{'jsonrpc': '2.0', 'method': 'eth_getProof', 'params': ['0x85854fe3853b7A51576bFd78564Ec1993f8820d1', ['0x01', '0x00'], 'latest'], 'id': 1}
```

##### function ethGetStorageAt(address sto, uint256 pos, tag)

```python
>>> JsonRPC.ethGetStorageAt("0x85854fe3853b7A51576bFd78564Ec1993f8820d1", "0x00", "4444")
{'jsonrpc': '2.0', 'method': 'eth_getStorageAt', 'params': ['0x85854fe3853b7A51576bFd78564Ec1993f8820d1', '0x00', '4444'], 'id': 1}
```

##### function web3Sha3(string to_hash_string)

```python
>>> JsonRPC.web3Sha3("12341254")
{'jsonrpc': '2.0', 'method': 'web3_sha3', 'params': ['12341254'], 'id': 64}
```

##### function ethMining()

```python
>>> JsonRPC.ethMining()
{'jsonrpc': '2.0', 'method': 'eth_mining', 'params': [], 'id': 71}
```

##### function ethAccounts()

```python
>>> JsonRPC.ethAccounts()
{'jsonrpc': '2.0', 'method': 'eth_accounts', 'params': [], 'id': 1}
```

##### function ethBlockNumber()

```python
>>> JsonRPC.ethBlockNumber()
{'jsonrpc': '2.0', 'method': 'eth_blockNumber', 'params': [], 'id': 1}
```

##### function ethGetCode(address addr)

```python
>>> JsonRPC.ethGetCode("0x85854fe3853b7A51576bFd78564Ec1993f8820d1")
{'jsonrpc': '2.0', 'method': 'eth_getCode', 'params': ['0x85854fe3853b7A51576bFd78564Ec1993f8820d1', 'latest'], 'id': 1}
```

##### function ethSign(address addr, string data)

```python
>>> JsonRPC.ethSign("0x85854fe3853b7A51576bFd78564Ec1993f8820d1", "123456")
{'jsonrpc': '2.0', 'method': 'eth_sign', 'params': ['0x85854fe3853b7A51576bFd78564Ec1993f8820d1', '123456'], 'id': 1}
```

##### function ethSendTransaction(json_object Transaction)

```python
>>> transaction = {
        "from": "0x7019fa779024c0a0eac1d8475733eefe10a49f3b",
        "to": "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e",
        "gas": "0x40000",
        "value": "0x20"
    }
>>> JsonRPC.ethSendTransaction(transaction)
{'jsonrpc': '2.0', 'method': 'eth_sendTransaction', 'params': [{'from': '0x7019fa779024c0a0eac1d8475733eefe10a49f3b', 'to': '0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e', 'gas': '0x40000', 'value': '0x20'}], 'id': 1}

```

##### function ethGetBlockByHash(uint256 blockhash, bool fullinfo)

```python
>>> JsonRPC.ethGetBlockByHash("0xfcaa6554604880ef255d502c542d8d66adb3358369cd3c81f3862615dd8d02a5", False)
{'jsonrpc': '2.0', 'method': 'eth_getBlockByHash', 'params': ['0xfcaa6554604880ef255d502c542d8d66adb3358369cd3c81f3862615dd8d02a5', False], 'id': 1}
```

##### function ethGetBlockByNumber(tag, bool fullinfo)

```python
>>> JsonRPC.ethGetBlockByNumber("latest", False)
{'jsonrpc': '2.0', 'method': 'eth_getBlockByNumber', 'params': ['latest', False], 'id': 1}
```

##### function ethGetTransactionReceipt(transactionhash)  

see the [sample 1](#Sample-One)

##### function send(url blockchain_address, headers hed, json data)

see the [sample 1](#Sample-One)

##### Sample One

```python
    host = 'http://127.0.0.1:8545'
    HTTP_HEADER = {'Content-Type': 'application/json'}
    transaction = {
        "from": "0x7019fa779024c0a0eac1d8475733eefe10a49f3b",
        "to": "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e",
        "gas": "0x40000",
        "value": "0x20"
    }
    packet_transaction = JsonRPC.ethSendTransaction(transaction)
    tx_response = JsonRPC.send(packet_transaction, HTTP_HEADER, host)
    tx_hash = tx_response['result']
    query = JsonRPC.ethGetTransactionReceipt(tx_hash)

    import time
    while True:
        time.sleep(1)
        tx_result = JsonRPC.send(query, HTTP_HEADER, host)
        if tx_result['result'] is None:
            continue
        else:
            print(tx_result['result'])
            break
```

Result:

```json
{
    "blockHash": "0xef6143f5d61453d6b797c3e927870b3bba942f2241631992f8b6505574c5ca17",
    "blockNumber": "0x1749",
    "contractAddress": ,
    "cumulativeGasUsed": "0x5208",
    "from": "0x7019fa779024c0a0eac1d8475733eefe10a49f3b",
    "gasUsed": "0x5208",
    "logs": [],
    "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "root": "0xc75f342199694bc79dfb59c7d12613cdc0291cc3a790d5db427b875c0607d845",
    "to": "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e",
    "transactionHash": "0x36543872f460d51bb5b46f1384d138384391b40bff1adfd9c6cf1a851a462c8f",
    "transactionIndex": "0x0"
}

```

##### Sample Two

```python
    query = JsonRPC.ethGetBlockByHash("0xfcaa6554604880ef255d502c542d8d66adb3358369cd3c81f3862615dd8d02a5", False)
    print(JsonRPC.send(query, HTTP_HEADER, host))
```

Result:

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "difficulty": "0x161a1b",
        "extraData": "0xda83010817846765746888676f312e31312e358777696e646f7773", 
        "gasLimit": "0xc276f3", 
        "gasUsed": "0x0",
        "hash": "0xfcaa6554604880ef255d502c542d8d66adb3358369cd3c81f3862615dd8d02a5", 
        "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "miner": "0x7019fa779024c0a0eac1d8475733eefe10a49f3b",
        "mixHash": "0x3a6b4fcc98406ff947789e9853db490d9bf0129e3ecb9bb3bdbc7c1a36228270",
        "nonce": "0x0fa86b002e272236",
        "number": "0x1745",
        "parentHash": "0x108c6d9f0725b57dc0039a6eb8568b24fc6859db85b78386ce53695dc069ec5f",
        "receiptsRoot": "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421",
        "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
        "size": "0x21c", 
        "stateRoot": "0xf80e263fe06bd2107f6911afeb67b8cf3d9512d6c1cff0910ce363c7a96de468",
        "timestamp": "0x5c849df1", 
        "totalDifficulty": "0xdf8570d8",
        "transactions": [],
        "transactionsRoot": "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421", 
        "uncles": []
    }
}
```

## Class Contract

Start with:

```python
from uiputils.eth import Contract
```

##### constructor(

#####     web3_handle,

#####     contract_address="",

#####     contract_abi/contract_abi_dir=None,

#####     contract_bytecode/contract bytecode_dir=None

##### )

The constructor doesn't deploy the contract. If the contract has been deployed, you can use the following functions.

##### property functions

An object of the functions in contract abi.

```python
>>> nsb.functions.isOwner(Web3.toChecksumAddress("0xe1300d8ea0909faa764c316436ad0ece571f62b2")).call()
False
```

Function call() helps execute the function.

##### attribute address

The address where the contract deployed at. 

##### attribute web3

The RPC-host which control the blockchain that the contract belongs to.

##### property abi

All the methods that the contract provides.

##### property bytecode

The .bin file content of the contract's code.

##### function funcs(void)

Return all the functions in the contract abi.

```python
>>> nsb.funcs()
[<Function addAction(bytes32,bytes32,bytes32)>, ...]
```

##### function func(string function_name, *args)

Execute the function in the contract abi.

```python
>>> nsb.func('isOwner', Web3.toChecksumAddress("0xe1300d8ea0909faa764c316436ad0ece571f62b2"))
False
```

## Class Network Status Blockchain

##### attribute handle

##### attribute web3

##### attribute prover

##### attribute proof_pool

##### attribute action_pool

##### property address

##### property tx

##### function getMekleProofByHash

##### function getMerkleProofByNumber

todo.

##### function watchProofPool

##### function proveProofs

##### function addAction

##### function getAction

##### function verifyAction

##### function validMerkleProoforNot

##### function getValidMerkleProof

##### function blockHeight

todo

##### function ownerVoted

todo

##### function start

todo

##### function stop

todo

##### function exec

todo

## Load Files

start with:

```python
from uiputils.eth import FileLoad
```

Sample:

```python
>>> FileLoad.getabi('./option_abi')
[{'constant': False, 'inputs': [{'name': '_proposal', 'type': 'uint256'}], 'name': 'buyOption', 'outputs': [], 'payable': True, 'stateMutability': 'payable', 'type': 'function'}, ...]
>>> FileLoad.getbytecode('./option_bytecode')
b'0x60806040526040516020806107908339810180604052810190808051906020019092919050505034678ac7230489e80000811015151561003e57600080fd5b34600081905550816001819055503360026000610100...'
```

# uiputils.*

## Types

### Class BlockchainNetwork

##### constructor(identifer="", rpc_port=0, data_dir="", listen_port=0, host="", public=False)

### Class SmartContract

##### constructor(bytecode="", domain="", name="", gas=hex(0), value=hex(0))

### Class StateProof

##### constructor(value, block, proof)



## Cast

start with:

```python
from uiptils.cast import *
```

##### function uintxstring(unsigned integer, size)

return x-bit string of number.

```python
>>> uintxstring(15, 8)
'00000015'
```

##### function uint32string(unsigned integer number)

return 32-bit string of number.

```python
>>> uintx32tring(15)
'00000000000000000000000000000015'
```

use `uint64string`, `uint128string`, `uint256string` in the same way.

## Go Types

start with:

```python
from uiputils.gotypes import *
```

### class GoInt8

the class of `int8`(Golang) in C.

```python
>>> x = GoInt8(15)
>>> x
c_byte(15)
```

use `GoInt16`,  `GoInt32`,  `GoInt64`, `GoUint8`, `GoUint16`, `GoUint32`, `GoUint64` in the same way.

If their is a go script:

```go
//export Sum
func Sum(x C.int, y C.int) C.int {
    return x + y
}
```

create go-cDLL and use the function in python:

```python
adder = CDLL(GODLLPATH).Sum
adder.argtypes = (GoInt32, GoInt32)
adder.restype = GoInt32
print(adder(1,2))
```

### class GoString

the class of `string` (Golang) in C.

##### property Type

return the type of GoString in C for setting the go-cDLL functions' arguments and results.

##### function fromstr(string)

cast the string in python to the `string` (Golang) in C.

If their is a go script:

```go
func _stringtoheaderkey(number uint64, hashstr string) []byte {
	return append(
        append(headerPrefix, uint64tobytes(number)...),
        stringtohash(hashstr).bytes()...
    )
}
// export stringtoheaderkey
func stringtoheaderkey(number C.ulonglong,hashstr *C.char) *C.char {
    res := _stringtoheaderkey(
        uint64(number),
        C.GoString(hashstr)
    )
    return C.Cbytes(res)
}
```

create go-cDLL and use the function in python:

```python
caster = CDLL(GODLLPATH).stringtoheaderkey
caster.argtypes = (GoUint32, GoString.Type)
caster.restype = GoBytes.Type
print(caster(1,GoString.fromstr("0x11e91152ab237ceff29728c03999ef2debadd7db0fc45b280657c6f7cc4c1ffa")))
```

### class GoStringSlice

the class of `string`(Golang) in C.

##### property Type

return the type of GoStringSlice in C for setting the go-cDLL functions' arguments and results.

##### function fromstrlist(string)

cast the stringlist in python to the `[]string` (Golang) in C.

### class GoBytes

the class of `[]Byte`(Golang) in C.

##### property Type

return the type of GoBytes in C for setting the go-cDLL functions' arguments and results.

##### function frombytes(bytes)

cast the bytes in python to the `[]byte` (Golang) in C.

[JSON-RPC]: https://github.com/ethereum/wiki/wiki/JSON-RPC
