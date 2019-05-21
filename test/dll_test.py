
# python modules
import time

# ethereum modules
from hexbytes import HexBytes

# uip modules
from uiputils.ethtools import JsonRPC, Prover

EDB_PATH = "D:/Go Ethereum/data/geth/chaindata"
url = "http://127.0.0.1:8545"
HTTP_HEADER = {'Content-Type': 'application/json'}
nsb_addr = "0x85854fe3853b7A51576bFd78564Ec1993f8820d1"


if __name__ == '__main__':
    response = JsonRPC.send(JsonRPC.eth_get_proof(nsb_addr, ["0x0"], "latest"), HTTP_HEADER, url)['result']
    storageProof = response['storageProof'][0]

    time.sleep(5)

    try:
        prover = Prover(EDB_PATH)

        # prover.verify(HexBytes(keccak(HexBytes(uint64hexstring(int(storageProof['key'], 16))))).hex(),
        #               storageProof['value'],
        #               response['storageHash'],
        #               storageProof['proof']
        #               )
        prover.close()
    except Exception:
        raise Exception

