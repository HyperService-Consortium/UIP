//link to Goleveldb
package main

import (
	"github.com/syndtr/goleveldb/leveldb"
	"fmt"
	"errors"
	"./rlp"
	"encoding/hex"
)

const EDB_PATH = "D:/Go Ethereum/data/geth/chaindata"


var (
	//Got LastHeader
	headHeaderKey = []byte("LastHeader")
	//Got LastBlock
	headBlockKey = []byte("LastBlock")
	//Got a BlockHeader
	headerPrefix = []byte("h")
)

//Hash byte-Array's length
const HashLength = 32

//char maps to bit integer
var hexmaps [128]uint64

//common.Hash
type Hash [HashLength]byte

func (h Hash) bytes() []byte { return h[ : ] }

//TODO - iterator
func checkAll(db *leveldb.DB){
	iter := db.NewIterator(nil, nil)
	for iter.Next(){
		key   := iter.Key()
		value := iter.Value()
		fmt.Println([]byte(key),[]byte(value))
	}
}

//unint64(8-bytes) to bytes
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

//input a string and return common.Hash
func stringtobytes(bytes string) []byte {
	glen := len(bytes)
	if  glen <= 1 || ((glen & 1) == 1) {
		return nil
	}
	glen >>= 1
	bres ,ofs := make([]byte, glen, glen), 0
	if bytes[1] == 'x' {
		ofs = 2
	}
	for idx := int(ofs); idx < glen; idx++ {
		bres[idx] |= byte(hexmaps[bytes[(idx + ofs) << 1 ]] << 4)
		bres[idx] |= byte(hexmaps[bytes[(idx + ofs) << 1 | 1]])
	}
	return bres
}

func stringtonibbles(nibbles string) []bytes {
	glen := len(nibbles)
	bres ,ofs := make([]byte, glen, glen), 0
	if nibbles[1] == 'x' {
		ofs = 2
	}
	for idx := int(ofs); idx < glen; idx++ {
		bres[idx] |= byte(hexmaps[nibbles[(idx + ofs)]])
	}
}

func stringtoheaderkey(number uint64, hashstr string) []byte {
	return append(append(headerPrefix, uint64toslice(number)...), stringtohash(hashstr).bytes()...);
}

func Cook(db *leveldb.DB, query []byte) ([]byte, error) {
	binfo, err := db.Get(query, nil)
	if err == nil {
		// fmt.Printf("[%x]\n",binfo)
		// fmt.Println("type:",reflect.TypeOf(binfo))
		// fmt.Printf("%x",binfo)
		// rlp.PrintListInString(rlp.Unserialize(binfo))
		return binfo, nil
	}else {
		fmt.Println("query error!", err)
		return nil, err
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
//2084db4a68aa8b172f70bc04e2e74541617c003374de6eb4b295e823e5beab01
//200decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563
//                 1
func findPath(db *leveldb.DB, rootHashStr *string, path []byte, storagepath []string, consumed uint32) ([]byte ,error) {
	roothash := stringtohash(*rootHashStr)
	querynode, err := Cook(db, roothash[ : ])
	if err != nil {
		return nil, err;
	}else {
		if hex.EncodeToString(querynode) != storagepath[0] {
			return nil, errors.New("No exists")
		}
		node := rlp.Unserialize(querynode)
		switch node.Length() {
			case 2: {
				firstvar, secondvar := node.Get(0).AsString(), node.Get(1).AsString()
				fmt.Println("Test", consumed, firstvar, secondvar)
				if len(path) == 30 {
					if hex.EncodeToString(path) != firstvar[consumed:] {
						return nil, errors.New("No exists")
					}
					return querynode, nil
				}
				return findPath(db, &secondvar, path[1 : ], storagepath[1 : ], consumed + 1)
			}
			case 17: {
				tryquery := node.Get(int(path[0])).AsString()
				if len(tryquery) == 64 {
					return findPath(db,&tryquery,path[1 : ], storagepath[1 : ], consumed + 1)
				}else{
					return nil, errors.New("No exists")
				}
			}
			default: {
				err := errors.New("Unknown node types")
				return nil, err
			}
		}
	}
}

func VerifyProof(db *leveldb.DB, rootHashStr *string, keyvalue *string, storagepath []string) {
	keyvaluelist := rlp.Unserialize(stringtobytes(*keyvalue))
	key, value := keyvaluelist.Get(0).AsString(), keyvaluelist.Get(1).AsString()
	fmt.Println(len(key))
	// key = append(make([]byte,0),2,9)
	toval, err := findPath(db, rootHashStr, stringtonibbles(key), storagepath, 0)
	fmt.Println("finally", toval, value, err)
	rlp.PrintListInString(rlp.Unserialize(toval))
}
func main(){
	//fmt.Println(stringtohash("6fb589682cc8db511886024d278b6712b4d886db988b5692e261ed4c9d709f8e").bytes())
	StorageHash := "0x11e91152ab237ceff29728c03999ef2debadd7db0fc45b280657c6f7cc4c1ffa"
	StorageProofPathVal := "e2a0200decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e56333"
	StoragePath := []string{"f8918080a06d032ff808e3a2b585df339916901d7b7d04c5bd18a088607093d3178172b7ee8080808080a0071b011fdbd4ad7d1e6f9762be4d1a88dffde614a6bd399bf3b5bad8f41249b5808080a01b56cc0a5b9b1ce34e9a14e896ea000c830bd64387573d238cbe3fa24ddfa2c3a0f5c2efa606e3a5be341f22bf1d5c8f4bce679719870c097a24abb38aec0a4855808080", "f8518080808080a06f643b8fd2176a403e2ccfae43808c4543289e1082078e91d821d1c7886d6f51808080a03822ab26403807d175522401e184b20b5aa8c7fcd802f4793970a70e810f4ce980808080808080", "e2a0200decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e56333"}
	//StoragePath := append(make([]byte,0),2,9)
	
	
	db, err := leveldb.OpenFile(EDB_PATH, nil)
	if err != nil{
		fmt.Println("link error")
		fmt.Println(err)
	}else {
		VerifyProof(db, &StorageHash, &StorageProofPathVal, StoragePath)
		db.Close()
	}
}
