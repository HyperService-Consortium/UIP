
from hexbytes import HexBytes
import rlp
# 001
node = "0x3175b7a638427703f0dbe7bb9bbf987a2551717b34e79f33b5b1008d1fa01db9"
# 0x3468288056310c82aa4c01a7e12a10f8111a0560e72b700555479031b86c357d

def TransIntoHex(nodelist):
    decodelist = []
    for node in nodelist:
        if isinstance(node, list):
            decodelist.append(TransIntoHex(node))
        elif isinstance(node, bytes):
            decodelist.append(HexBytes(node).hex())
        else:
            raise TypeError("node must be str or list, But %s." % node.__name__)
    return decodelist


if __name__ == "__main__":
    print(TransIntoHex(rlp.decode(HexBytes(node))))
