//link to Goleveldb
package main

import (
	"github.com/syndtr/goleveldb/leveldb"
	"fmt"
	"errors"
	"./rlp"
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
func findPath(db *leveldb.DB, rootHashStr string,path []byte) ([]byte ,error) {
	roothash := stringtohash(rootHashStr)
	querynode, err := Cook(db, roothash[ : ])
	if err != nil {
		return nil, err;
	}else {
		if len(path) == 0 {
			return querynode, nil
		}
		node := rlp.Unserialize(querynode)
		switch node.Length() {
			case 2: {
				return findPath(db,node.Get(1).AsString(),path[1 : ])
				break ;
			}
			case 17: {
				tryquery := node.Get(int(path[0])).AsString()
				if len(tryquery) == 64 {
					return findPath(db,tryquery,path[1 : ])
				}else{
					err = errors.New("No exists")
					return nil, err
				}
				break ;
			}
			default: {
				err := errors.New("Unknown node types")
				return nil, err
			}
		}
	}
	err = errors.New("Impossible approach")
	return nil, err
}
func VerifyProof(db *leveldb.DB, rootHashStr string, key []byte){
	toval, err := findPath(db, rootHashStr, key)
	fmt.Println(toval, err)
	rlp.PrintListInString(rlp.Unserialize(toval))
}
func main(){
	//fmt.Println(stringtohash("6fb589682cc8db511886024d278b6712b4d886db988b5692e261ed4c9d709f8e").bytes())
	StorageHash := "0x11e91152ab237ceff29728c03999ef2debadd7db0fc45b280657c6f7cc4c1ffa"
	//StorageProofPathVal := "e2a0200decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e56333"
	//StoragePath := []string{"f8918080a06d032ff808e3a2b585df339916901d7b7d04c5bd18a088607093d3178172b7ee8080808080a0071b011fdbd4ad7d1e6f9762be4d1a88dffde614a6bd399bf3b5bad8f41249b5808080a01b56cc0a5b9b1ce34e9a14e896ea000c830bd64387573d238cbe3fa24ddfa2c3a0f5c2efa606e3a5be341f22bf1d5c8f4bce679719870c097a24abb38aec0a4855808080", "f8518080808080a06f643b8fd2176a403e2ccfae43808c4543289e1082078e91d821d1c7886d6f51808080a03822ab26403807d175522401e184b20b5aa8c7fcd802f4793970a70e810f4ce980808080808080", "e2a0200decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e56333"}
	StoragePath := append(make([]byte,0),2,9)
	fmt.Println("My first leveldb")
	//rlp.PrintListInString(rlp.Unserialize(stringtobytes("e2a0200decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e56333")))
	db, err := leveldb.OpenFile(EDB_PATH, nil)
	if err != nil{
		fmt.Println("link error")
		fmt.Println(err)
	}else {
		//checkAll(db)
		// que, err := Cook(db,stringtohash("11e91152ab237ceff29728c03999ef2debadd7db0fc45b280657c6f7cc4c1ffa").bytes())
		// if err == nil {
		// 	rlp.PrintListInString(rlp.Unserialize(que))
		// }else {
		// 	fmt.Println(err)
		// }
		VerifyProof(db, StorageHash, StoragePath)
		db.Close()
	}
}
/*
 */
/*
    6d032ff808e3a2b585df339916901d7b7d04c5bd18a088607093d3178172b7ee
["0x200decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563","0x33"]
[104 0 0 0 0 0 0 0 19 0 153 250 248 6 134 246 32 178 249 33 18 247 117 246 40 96 249 33 67 115 148 25 248 49 247 250 117 121 5 17 246]
[104 0 0 0 0 0 0 0 19 0 153  94 236 6 134 106 32 242 189 33 18 107 117 58 40 96 253 33 67 179 148 25 12 49 251 46 117 121 5 17 10 116]
 */