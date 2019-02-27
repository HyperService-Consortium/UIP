package rlp
import(
	"fmt"
	"errors"
	"encoding/hex"
)
const(
	NIL = iota
	BYTES
	GLIST
)

type Atom interface{}
type Glist struct {
	dat Atom
	typeId int
}
func makeGlistContentGlist() *Glist {
	return &Glist{dat: make([]Atom, 0, 65535), typeId: 2}
}
func makeGlistContentBytes(data []byte) *Glist {
	return &Glist{dat: data, typeId: 1}
}
func (g *Glist) Type() int{
	return g.typeId
}
func _Unserialize(dtr []byte) []Atom {
	atomList := make([]Atom, 0, 65535)
	if len(dtr) == 0 {
		return atomList
	}
	if(dtr[0] < 128){
		return append(append(atomList, makeGlistContentBytes(dtr[0 : 1])), _Unserialize(dtr[1 : ])...)
	}else if dtr[0] < 184 {
		return append(append(atomList, makeGlistContentBytes(dtr[1 : dtr[0] - 127])), _Unserialize(dtr[dtr[0] - 127 : ])...)
	}else if dtr[0] < 192 {
		// dlen = truelen + 1
		dlen := int(dtr[0]) - 182
		tlen := decodelength(dtr[1 : dlen])
		return append(append(atomList, makeGlistContentBytes(dtr[dlen : dlen + tlen])), _Unserialize(dtr[dlen + tlen : ])...)
		//return &Glist{dat:, typeId: 1}
	}else if dtr[0] < 248 {
		// dlen = truelen + 1
		return append(append(atomList, Unserialize(dtr[0 : dtr[0] - 191])), _Unserialize(dtr[dtr[0] - 191 : ])...)
	}else {
		// dlen = truelen + 1
		dlen := int(dtr[0]) - 246
		tlen := decodelength(dtr[1 : dlen])
		// fmt.Println("here",dlen,decodelength(dtr[1 : dlen]))
		return append(append(atomList, Unserialize(dtr[0 : dlen + tlen])), _Unserialize(dtr[dlen + tlen : ])...)
	}
	return atomList
}
func Unserialize(dtr []byte) *Glist {
	if len(dtr) == 0 {
		return makeGlistContentGlist()
	}
	if(dtr[0] < 128){
		if len(dtr) > 1 {
			err := errors.New("superflours")
			fmt.Println(err)
			return nil
		}
		return makeGlistContentBytes(dtr[0 : ])
	}else if dtr[0] < 184 {
		if len(dtr) > int(dtr[0] - 127) {
			err := errors.New("superflours")
			fmt.Println(err)
			return nil
		}
		return makeGlistContentBytes(dtr[1 : ])
	}else if dtr[0] < 192 {
		// dlen = truelen + 1
		//must be uint32, but int for convenience
		dlen := int(dtr[0]) - 182
		tlen := decodelength(dtr[1 : dlen])
		if len(dtr) > tlen + dlen {
			err := errors.New("superflours")
			fmt.Println(err)
			return nil
		}
		//fmt.Println(decodelength(dtr[1 : dlen]))
		return makeGlistContentBytes(dtr[dlen : ])
		//return &Glist{dat:, typeId: 1}
	}else if dtr[0] < 248 {
		// dlen = truelen + 1
		// fmt.Println(dtr[0] - 191)
		if len(dtr) > int(dtr[0] - 191) {
			err := errors.New("superflours")
			fmt.Println(err)
			return nil
		}
		return &Glist{dat: _Unserialize(dtr[1 : ]), typeId: 2}
	}else {
		// dlen = truelen + 1
		//must be uint32, but int for convenience
		dlen := int(dtr[0]) - 246
		tlen := decodelength(dtr[1 : dlen])
		if len(dtr) > tlen + dlen {
			err := errors.New("superflours")
			fmt.Println(err)
			return nil
		}
		return &Glist{dat: _Unserialize(dtr[dlen : ]), typeId: 2}
	}
}
func decodelength(dtr []byte) int {
	var len int
	for _, t := range dtr {
		len = (len<<4) | int(t)
	}
	return len
}
func PrintList(g *Glist){
	if g == nil {
		fmt.Print("[]")
		return ;
	}
	switch g.typeId {
		case 1:{
			fmt.Print(g.dat.([]byte))
			break ;
		}
		case 2:{
			fmt.Print("[")
			for i, v := range(g.dat.([]Atom)) {
				if i != 0 {
					fmt.Print(",")
				}
				PrintList(v.(*Glist))
			}
			fmt.Print("]")
			break;
		}
		default :{
			break ;
		}
	}
}
func PrintListInString(g *Glist){
	if g == nil {
		fmt.Print("~")
		return ;
	}
	switch g.typeId {
		case 1:{
			fmt.Print("\"0x"+hex.EncodeToString(g.dat.([]byte))+"\"")
			break ;
		}
		case 2:{
			fmt.Print("[")
			for i, v := range(g.dat.([]Atom)) {
				if i != 0 {
					fmt.Print(",")
				}
				PrintListInString(v.(*Glist))
			}
			fmt.Print("]")
			break;
		}
		default :{
			break ;
		}
	}
}
func (g *Glist) Get(ref int) *Glist {
	return g.dat.([]Atom)[ref].(*Glist)
}
func (g *Glist) AsBytes() []byte {
	return g.dat.([]byte)
}
func (g *Glist) AsString() string {
	return hex.EncodeToString(g.dat.([]byte))
}
func (g *Glist) Length() int {
	if g.typeId == 1 {
		return len(g.dat.([]byte))
	}else if g.typeId == 2 {
		return len(g.dat.([]Atom))
	}else {
		return -1
	}
}
func main(){
	// var t []byte
	// // t = append(t, 0xf8, 2, 33, 35, 37)
	// // t = append(t, 0xc7, 0x83, 33, 35, 37, 0x82 , 32 , 33)
	// // t = append(t,0xc7, 0xc0, 0xc1, 0xc0, 0xc3, 0xc0, 0xc1, 0xc0)
	// t=append(t, 0xf8, 0xc7, 0xc0, 0xc1, 0xc0, 0xc3, 0xc0, 0xc1, 0xc0)
	// // for i := 0 ;i < 56 ; i++ {
	// // 	t = append(t, 123)
	// // }
	// fmt.Println(t)
	// // var quer,qq Glist
	// var qq *Glist
	// qq = Unserialize(t)
	// //fmt.Println((qq.dat.([]Atom))[0])
	// //makeGlistContentBytes([]byte("21241241"))
	// PrintList(qq)
}
/*
[[],[[]],[[],[[]]]]
[[],[[]],[[],[[]]]]
 */