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
