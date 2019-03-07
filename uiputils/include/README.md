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

