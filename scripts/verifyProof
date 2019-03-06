//link to Goleveldb
package main

import (
	"github.com/syndtr/goleveldb/leveldb"
	"fmt"
	"errors"
	"./rlp"
	"encoding/hex"
)

const (
	EDB_PATH = "D:/Go Ethereum/data/geth/chaindata"
	SHORTNODE = 2
	FULLNODE = 17
	HASHSTRINGLENGTH = 64
)


var (
	//Got LastHeader
	headHeaderKey = []byte("LastHeader")
	//Got LastBlock
	headBlockKey = []byte("LastBlock")
	//Got a BlockHeader
	headerPrefix = []byte("h")
)

// Hash byte-Array's length
const HashLength = 32

// char maps to bit integer
var hexmaps [128]uint64

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
func uint64toslice(number uint64) []byte {
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

	if bytes[1] == 'x' {
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
	if nibbles[1] == 'x' {
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
	return append(append(headerPrefix, uint64toslice(number)...), stringtohash(hashstr).bytes()...);
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

// get value of key on the trie
func findPath(db *leveldb.DB, rootHashStr string, path string, storagepath []string, consumed int) (string ,error) {

	//key consumed
	if len(path) == 0 {
		return "", errors.New("No exists")
	}

	// get node from db
	querynode, err := db.Get(stringtohash(rootHashStr).bytes(), nil)
	if err != nil {
		return "", err;
	}else {

		// compare to storagepath
		if hex.EncodeToString(querynode) != storagepath[0] {
			return "", errors.New("No exists")
		}

		node := rlp.Unserialize(querynode)

		switch node.Length() {
			case SHORTNODE: {
				firstvar, secondvar := node.Get(0).AsString(), node.Get(1).AsString()

				//end of proofpath
				if len(storagepath) == 1 {
					if path != firstvar[consumed:] {
						return "", errors.New("No exists")
					}
					return secondvar, nil
				}

				//compare prefix of the path with node[0]
				firstvarlen := len(firstvar)
				if (firstvarlen > len(path)) || (firstvar != path[0:firstvarlen]) {
					return "", errors.New("No exists")
				}

				return findPath(db, secondvar, path[firstvarlen: ], storagepath[1 : ], consumed + firstvarlen)
			}
			case FULLNODE: {
				tryquery := node.Get(int(hexmaps[path[0]])).AsString()

				if len(tryquery) == HASHSTRINGLENGTH {
					return findPath(db, tryquery, path[1 : ], storagepath[1 : ], consumed + 1)
				}else {
					return "", errors.New("No exists")
				}
			}
			default: {
				return "", errors.New("Unknown node types")
			}
		}
	}
}

func VerifyProof(db *leveldb.DB, rootHashStr string, key string, value string, storagepath []string) {
	if key[0:2] == "0x" {
		key = key[2:]
	}
	if value[0:2] == "0x" {
		value = value[2:]
	}
	// key = append(make([]byte,0),2,9)
	toval, err := findPath(db, rootHashStr, key, storagepath, 0)
	if err != nil {
		fmt.Println(err)
	}else {
		if value == toval {
			fmt.Println("Proved")
		}else {
			fmt.Println("key maps to", "0x" + toval + ", not", "0x" + value)
		}
	}
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
	StorageHash := "0x11e91152ab237ceff29728c03999ef2debadd7db0fc45b280657c6f7cc4c1ffa"
	StoragePath := []string{"f8918080a06d032ff808e3a2b585df339916901d7b7d04c5bd18a088607093d3178172b7ee8080808080a0071b011fdbd4ad7d1e6f9762be4d1a88dffde614a6bd399bf3b5bad8f41249b5808080a01b56cc0a5b9b1ce34e9a14e896ea000c830bd64387573d238cbe3fa24ddfa2c3a0f5c2efa606e3a5be341f22bf1d5c8f4bce679719870c097a24abb38aec0a4855808080", "f8518080808080a06f643b8fd2176a403e2ccfae43808c4543289e1082078e91d821d1c7886d6f51808080a03822ab26403807d175522401e184b20b5aa8c7fcd802f4793970a70e810f4ce980808080808080", "e2a0200decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e56333"}

	key := "0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563"
	val := "0x33"
	
	db, err := leveldb.OpenFile(EDB_PATH, nil)
	if err != nil {
		fmt.Println("link error")
		fmt.Println(err)
	}else {
		VerifyProof(db, StorageHash, key, val, StoragePath)
		db.Close()
	}
}
