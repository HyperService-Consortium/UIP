//link to Goleveldb
package main

import (
	"github.com/syndtr/goleveldb/leveldb"
	"fmt"
	"./rlp"
	"encoding/hex"
)

const (
	EDB_PATH = "D:/Go Ethereum/data/geth/chaindata"
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
	return append(append(headerPrefix, uint64tobytes(number)...), stringtohash(hashstr).bytes()...);
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

func main() {
	rootHashStr := "0xab87a50da179c4b4be23614f87cb4bdc47ccdbbdc50e44365ff48c209c8505cac"

	db, err := leveldb.OpenFile(EDB_PATH, nil)
    if err != nil {
		fmt.Println("link error")
        fmt.Println(err)
	}else {
		defer db.Close()
		querynode, err := db.Get(stringtohash(rootHashStr).bytes(), nil)
		if err != nil {
			fmt.Println("query error")
			fmt.Println(err)
		}else {
			fmt.Println(querynode)
			node := rlp.Unserialize(querynode)
			fmt.Println(hex.EncodeToString(querynode))
			rlp.PrintListInString(node)
		}
	}
}
