//link to Goleveldb
package main

import (
	"github.com/syndtr/goleveldb/leveldb"
	"fmt"
	"errors"
	"./rlp"
    "encoding/hex"
    "C"
	"unsafe"
	"strconv"
)

const (
	// test-db dir
	EDB_PATH = "D:/Go Ethereum/data/geth/chaindata"
	// size of a secure-MPT's short-node
	SHORTNODE = 2
	// size of a secure-MPT's full-node
	FULLNODE = 17
	// length of a keccak256hash in string (16^64 = 256^32)
	HASHSTRINGLENGTH = 64
	// bytes of a char* (C pointer)
	CHAR_P_SIZE = 8
	// max number of onload-dbs
	MXONLOADDB = 64
	// Hash byte-Array's length
	HashLength = 32
)


var (
	//Got LastHeader
	headHeaderKey = []byte("LastHeader")
	//Got LastBlock
	headBlockKey = []byte("LastBlock")
	//Got a BlockHeader
	headerPrefix = []byte("h")
	//onload-db array
	dbPacket = make([]*leveldb.DB, 0, MXONLOADDB)
	//dbfree reference
	dbpi = 0
	// char maps to bit integer
	hexmaps [128]uint64
)


// common.Hash
type Hash [HashLength]byte

func (h Hash) bytes() []byte { return h[ : ] }

// TODO - iterator
func checkAll(db *leveldb.DB){
	iter := db.NewIterator(nil, nil)
	for iter.Next(){
		key   := iter.Key()
		value := iter.Value()
		fmt.Println([]byte(key),[]byte(value))
	}
}

// unint64(8-bytes) to bytes
func uint64tobytes(number uint64) []byte {
	enc := make([]byte, 8)
	for idx := uint64(0); idx < 8; idx++ {
		enc[7 - idx] = byte((number >> (idx << 3) ) & 0xff)
	}
	//fmt.Println(enc);
	return enc
}

//input a string and return common.Hash
func stringtohash(hashstr string) Hash {
	var hres Hash
	ofs := uint64(0)

	if hashstr[1] == 'x' {
		ofs = 1
	}

	for idx	:= uint64(0); idx < 32; idx++ {
		hres[idx] |= byte(hexmaps[hashstr[ (idx + ofs) << 1     ]] << 4)
		hres[idx] |= byte(hexmaps[hashstr[((idx + ofs) << 1) | 1]])
	}
	return hres
}

//input a string and return a byte slice
func stringtobytes(bytes string) []byte {
	glen := len(bytes)
	if  glen <= 1 || ((glen & 1) == 1) {
		return nil
	}

	glen >>= 1
	ofs := 0

	if len(bytes) >= 2 &&  bytes[1] == 'x' {
		ofs = 1
	}

	glen -= ofs

	bres := make([]byte, glen, glen)
	for idx := 0; idx < glen; idx++ {
		bres[idx] |= byte(hexmaps[bytes[(idx + ofs) << 1 ]] << 4)
		bres[idx] |= byte(hexmaps[bytes[(idx + ofs) << 1 | 1]])
	}
	return bres
}

//input a string and return a nibble slice
func stringtonibbles(nibbles string) []byte {
	glen := len(nibbles)

	ofs := 0
	if len(nibbles) >= 2 &&  nibbles[1] == 'x' {
		ofs = 2
	}
	glen -= ofs

	bres := make([]byte, glen, glen)
	for idx := 0; idx < glen; idx++ {
		bres[idx] = byte(hexmaps[nibbles[idx + ofs]])
	}
	return bres
}

// input a block number and the corresponding block hash, return a headerkey
func stringtoheaderkey(number uint64, hashstr string) []byte {
	return append(append(headerPrefix, uint64tobytes(number)...), stringtohash(hashstr).bytes()...);
}

// input a char*[] and return string[] (slice)
func stringPtrToStringSlice(stringPtr **C.char, slicelen C.size_t) []string {
    strslice := make([]string, 0, slicelen)
    var unblock unsafe.Pointer
    
    for idx := C.size_t(0); idx < slicelen; idx++ {
        unblock = unsafe.Pointer(uintptr(unsafe.Pointer(stringPtr)) + uintptr(idx * CHAR_P_SIZE))
        strslice = append(strslice, C.GoString(*((**C.char)(unblock))))
    }
    return strslice;
}

// compare two byte slice
func bytesequal(nib1 []byte, nib2 []byte) bool {
	len1, len2 := len(nib1), len(nib2)
	if len1 != len2 {
		return false
	}
	for idx := 0; idx < len1 ; idx++ {
		if nib1[idx] != nib2[idx] {
			return false
		}
	}
	return true
}

// compare to hexstring without leading-zero
func hexstringequal(hexx string, hexy string) bool {
	var ofsx, ofsy = 0, 0
	if len(hexx) >= 2 &&  hexx[0:2] == "0x" {
		ofsx = 2
	}
	if len(hexy) >= 2 &&  hexy[0:2] == "0x" {
		ofsy = 2
	}
	var lenx, leny int
	for lenx = len(hexx) - 1 ; ofsx < lenx && (hexx[ofsx] == '0') ; ofsx++ {

	}
	
	for leny = len(hexy) - 1 ; ofsy < leny && (hexy[ofsy] == '0') ; ofsy++ {

	}
	return hexx[ofsx:] == hexy[ofsy:]
}


//export OpenDB
func OpenDB(dbpath *C.char) C.int {
    db, err := leveldb.OpenFile(C.GoString(dbpath), nil)
    if err != nil {
		fmt.Println("link error")
        fmt.Println(err)
        return C.int(0)
	}else {
        dbPacket = append(dbPacket, db)
        dbpi++
		return C.int(dbpi - 1);
	}
    
}


//export CloseDB
func CloseDB(dbpi C.int) {
    db := dbPacket[dbpi]
    db.Close();
}


// get value of key on the trie
func findPath(db *leveldb.DB, roothash string, path string, storagepath []string, consumed int) (string, error) {

	//key consumed
	if len(path) == 0 {
		return "", errors.New("consumed")
	}

	// get node from db
	querynode, err := db.Get(stringtohash(roothash).bytes(), nil)
	if err != nil {
		return "", err;
	}else {

		// compare to storagepath
		if hex.EncodeToString(querynode) != storagepath[0] {
			return "", errors.New("No exists(differ from path), in depth" + strconv.FormatInt(int64(consumed), 10) + ", querying"+ roothash)
		}

		node := rlp.Unserialize(querynode)

		switch node.Length() {
			case SHORTNODE: {
				firstvar, secondvar := node.Get(0).AsString(), node.Get(1).AsString()

				//end of proofpath
				if len(storagepath) == 1 {
					if path != firstvar[consumed:] {
						return "", errors.New("No exists(no this branch), in depth" + strconv.FormatInt(int64(consumed), 10) + ", querying"+ roothash)
					}
					return secondvar, nil
				}

				//compare prefix of the path with node[0]
				firstvarlen := len(firstvar)
				if (firstvarlen > len(path)) || (firstvar != path[0:firstvarlen]) {
					return "", errors.New("No exists(no this branch), in depth" + strconv.FormatInt(int64(consumed), 10) + ", querying"+ roothash)
				}

				return findPath(db, secondvar, path[firstvarlen: ], storagepath[1 : ], consumed + firstvarlen)
			}
			case FULLNODE: {
				tryquery := node.Get(int(hexmaps[path[0]])).AsString()

				if len(tryquery) == HASHSTRINGLENGTH {
					return findPath(db, tryquery, path[1 : ], storagepath[1 : ], consumed + 1)
				}else {
					return "", errors.New("No exists, in depth" + strconv.FormatInt(int64(consumed), 10) + ", querying"+ roothash)
				}
			}
			default: {
				return "", errors.New("Unknown node types")
			}
		}
	}
}


func _VerifyProof(db *leveldb.DB, rootHashStr string, key string, value string, storagepath []string) bool {
	if len(key) >= 2 && key[0:2] == "0x" {
		key = key[2:]
	}
	if len(value) >= 2 && value[0:2] == "0x" {
		value = value[2:]
	}
	for _, str := range(storagepath) {
		if len(str) >= 2 && str[0:2] == "0x" {
			str = str[2:]
		}
	}

	// key = append(make([]byte,0),2,9)
	toval, err := findPath(db, rootHashStr, key, storagepath, 0)
	if err != nil {
		fmt.Println(err)
	}else {
		if hexstringequal(value, toval) == true {
            fmt.Println("Proved")
            return true
		}else {
            fmt.Println("key maps to", "0x" + toval + ", not", "0x" + value)
            return false
		}
    }
    return false
}
//export VerifyProof
func VerifyProof(dbPtr C.int,
                rootHashStrPtr *C.char, keyPtr *C.char, valuePtr *C.char,
                storagepathSlice **C.char, storagepathSliceLen C.size_t) C.int {
    db := dbPacket[dbPtr]
    rootHashStr := C.GoString(rootHashStrPtr)
    key := C.GoString(keyPtr)
    value := C.GoString(valuePtr)
    storagepath := stringPtrToStringSlice(storagepathSlice, storagepathSliceLen)

    if _VerifyProof(db, rootHashStr, key, value, storagepath) {
        return 1
    }
    return 0
}

func verifyKey(db *leveldb.DB, roothash string, path string, consumed int) (string, error) {
	
	//key consumed
	if len(path) == 0 {
		return "", errors.New("consumed")
	}

	// get node from db
	querynode, err := db.Get(stringtohash(roothash).bytes(), nil)
	if err != nil {
		return "", err;
	}else {

		// compare to storagepath
		// compare to rlp-hash
		// TODO

		node := rlp.Unserialize(querynode)

		switch node.Length() {
			case SHORTNODE: {
				firstvar, secondvar := node.Get(0).AsString(), node.Get(1).AsString()

				//end of proofpath
				if path == firstvar[consumed:] {
					return secondvar, nil
				}

				//compare prefix of the path with node[0]
				firstvarlen := len(firstvar)
				if (firstvarlen > len(path)) || (firstvar != path[0:firstvarlen]) {
					return "", errors.New("No exists(no this branch), in depth" + strconv.FormatInt(int64(consumed), 10) + ", querying"+ roothash)
				}

				return verifyKey(db, secondvar, path[firstvarlen: ], consumed + firstvarlen)
			}
			case FULLNODE: {
				tryquery := node.Get(int(hexmaps[path[0]])).AsString()

				if len(tryquery) == HASHSTRINGLENGTH {
					return verifyKey(db, tryquery, path[1 : ], consumed + 1)
				}else {
					return "", errors.New("No exists, in depth" + strconv.FormatInt(int64(consumed), 10) + ", querying"+ roothash)
				}
			}
			default: {
				return "", errors.New("Unknown node types")
			}
		}
	}
}

func _VerifyProofWithoutPath(db *leveldb.DB, rootHashStr string, key string, value string) bool {
	if len(key) >= 2 && key[0:2] == "0x" {
		key = key[2:]
	}
	if len(value) >= 2 && value[0:2] == "0x" {
		value = value[2:]
	}

	// key = append(make([]byte,0),2,9)
	toval, err := verifyKey(db, rootHashStr, key, 0)
	if err != nil {
		fmt.Println(err)
	}else {
		if hexstringequal(value, toval) == true {
            fmt.Println("Proved")
            return true
		}else {
            fmt.Println("key maps to", "0x" + toval + ", not", "0x" + value)
            return false
		}
    }
    return false
}
//export VerifyProofWithoutPath
func VerifyProofWithoutPath(dbPtr C.int, rootHashStrPtr *C.char, keyPtr *C.char, valuePtr *C.char) C.int {
    db := dbPacket[dbPtr]
    rootHashStr := C.GoString(rootHashStrPtr)
    key := C.GoString(keyPtr)
    value := C.GoString(valuePtr)

    if _VerifyProofWithoutPath(db, rootHashStr, key, value) {
        return 1
    }
    return 0
}

func init() {
	for idx := '0'; idx <= '9'; idx++ {
		hexmaps[idx] = uint64(idx - '0')
	}
	for idx := 'a'; idx <= 'f'; idx++ {
		hexmaps[idx] = uint64(idx - 'a' + 10)
	}
	for idx := 'A'; idx <= 'F'; idx++ {
		hexmaps[idx] = uint64(idx - 'A' + 10)
	}
}

func main(){
}
