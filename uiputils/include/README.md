## Verity Proof

##### function openDB(dbpath *C.char) returns(C.int)

open an ethereum chain database and return an index integer of the Go-levelDB pointer.

##### function closeDB(dbpi C.int) returns(none)

##### func VerifyProof(

##### dbPtr C.int,

##### rootHashStrPtr *C.char,

#####  keyPtr *C.char,

#####  valuePtr *C.char,

##### storagepathSlice **C.char,

#####  storagepathSliceLen C.size_t

##### ) returns(C.int)

in go, the function looks like:

```go
func _VerifyProof(db *leveldb.DB, rootHashStr string, key string, value string, storagepath []string) bool
```

If we use JSON-RPC method ([eth_getProof][ethGetProof]), for example

In geth (go-ethereum js-console):

```javascript
> eth.getProof("0xd7ea2b03da511799eb0c5a28989cf5268c869311", ["0x0"], "latest")
```

Or in python with `uiputils.eth.JsonRPC`:

```python
>>> from uiputils.eth import JsonRPC
>>> url = "http://127.0.0.1:8545"
>>> hed = {'Content-Type': 'application/json'}
>>> dat = json.dumps(JsonRPC.ethGetProof("0xd7ea2b03da511799eb0c5a28989cf5268c869311", ["0x0"], "latest"))
>>> requests.post(url,headers=hed,data=dat).json()
```

then we get:

```javascript
{
  accountProof: 
  ...
  ...
  storageHash: "0x11e91152ab237ceff29728c03999ef2debadd7db0fc45b280657c6f7cc4c1ffa",
  storageProof: [{
      key: "0x0",
      proof: ["0xf8918080a06d032ff808e3a2b585df339916901d7b7d04c5bd18a088607093d3178172b7ee8080808080a0071b011fdbd4ad7d1e6f9762be4d1a88dffde614a6bd399bf3b5bad8f41249b5808080a01b56cc0a5b9b1ce34e9a14e896ea000c830bd64387573d238cbe3fa24ddfa2c3a0f5c2efa606e3a5be341f22bf1d5c8f4bce679719870c097a24abb38aec0a4855808080", "0xf8518080808080a06f643b8fd2176a403e2ccfae43808c4543289e1082078e91d821d1c7886d6f51808080a03822ab26403807d175522401e184b20b5aa8c7fcd802f4793970a70e810f4ce980808080808080", "0xe2a0200decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e56333"],
      value: "0x33"
  }]
}
```



[ethGetProof]:https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getproof