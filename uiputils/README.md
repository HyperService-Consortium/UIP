# uiputils.eth

## JSON-RPC

start with:

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

## Class Contract

start with:

```python
from uiputils.eth import Contract
```

##### constructor(

##### 	web3handle,

##### 	contract address="",

##### 	contract abi/contract abi address=None,

##### 	contract bytecode/contract bytecode address=None

##### )

The constructor doesn't deploy the contract. If the contract has been deployed, you can use the following functions.

##### attribute functions

a object of the functions in contract abi.

```python
>>> nsb.functions.isOwner(Web3.toChecksumAddress("0xe1300d8ea0909faa764c316436ad0ece571f62b2")).call()
False
```

function call() helps execute the function.

##### attribute address

##### attribute web3

##### attribute abi

##### attribute bytecode

##### function funcs(void)

return all the functions in contract abi

```python
>>> nsb.funcs()
[<Function addAction(bytes32,bytes32,bytes32)>, ...]
```

##### function func(string functions name, *args)

```python
>>> nsb.func('isOwner', Web3.toChecksumAddress("0xe1300d8ea0909faa764c316436ad0ece571f62b2"))
False
```

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

##### attribute Type

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

##### attribute Type

return the type of GoStringSlice in C for setting the go-cDLL functions' arguments and results.

##### function fromstrlist(string)

cast the stringlist in python to the `[]string` (Golang) in C.

### class GoBytes

the class of `[]Byte`(Golang) in C.

##### attribute Type

return the type of GoBytes in C for setting the go-cDLL functions' arguments and results.

##### function frombytes(bytes)

cast the bytes in python to the `[]byte` (Golang) in C.

[JSON-RPC]:https://github.com/ethereum/wiki/wiki/JSON-RPC