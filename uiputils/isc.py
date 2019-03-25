
import rlp

from hexbytes import HexBytes
from eth_hash.auto import keccak

# uip modules
from uiputils.uiperror import Missing
from uiputils.uiptypes import Transaction

from uiputils.eth.tools import AbiEncoder
from uiputils.eth.tools import FileLoad, JsonRPC
from uiputils.eth.ethtypes import InsuranceSmartContract as ethISC

from uiputils.config import ETHSIGN_HEADER, INCLUDE_PATH
ENC = 'utf-8'


class InsuranceSmartContract:
    def __init__(
        self,
        msg=None,
        signature=None,
        owners=None,
        ves=None,
        tx_head=None,
        contract_addr=None
    ):
        # Insurance Smart Contract is a contract on the blockchain
        # TODO : contract construct
        if contract_addr is None:
            if msg is None or signature is None or owners is None or ves is None:
                self.address = None
            else:
                msg = HexBytes(msg)
                print(
                    owners, ',',
                    [0, 0, 0], ',',
                    HexBytes(ETHSIGN_HEADER + bytes(str(len(msg)).encode(ENC)) + bytes(msg)).hex(), ',',
                    signature, ',',
                    HexBytes(keccak(ETHSIGN_HEADER + b'\x31\x33\x30' + bytes(signature[2:].encode(ENC)))).hex(), ',',
                    3
                )
                encoded_data = AbiEncoder.encodes(
                    [
                        owners,
                        [0, 0, 0],
                        HexBytes(ETHSIGN_HEADER + bytes(str(len(msg)).encode(ENC)) + bytes(msg)).hex(),
                        signature,
                        keccak(ETHSIGN_HEADER + b'\x31\x33\x30' + bytes(signature[2:].encode(ENC))),
                        3
                    ],
                    ['address[]', 'uint256[]', 'bytes', 'bytes', 'bytes32', 'uint256']
                )
                bytescode = FileLoad.getbytecode('../isc/isc.bin')
                ves.unlockself()
                tx_json = JsonRPC.eth_send_transaction({
                    'from': ves.address,
                    'data': bytescode.decode(ENC) + encoded_data,
                    'gas': hex(8000000)
                })
                # print(tx_json)
                response = JsonRPC.send(tx_json, rpc_host=ves.chain_host)
                print(response)
        else:
            self.address = contract_addr
        self.owners = owners
        self.handle = ethISC(ves.chain_host, self.address, INCLUDE_PATH + '/isc.abi', tx_head)

    def update_TxInfo(self, tx: Transaction):
        tx_info = tx.tx_info
        print(tx_info)

    def update_funds(self, owner, fund):
        if owner not in self.owners:
            raise Missing('this address is not owner')
        print(owner, "updated fund:", fund)

    def insurance_claim(self, contract_id, atte):
        pass

    def settle_contract(self, contract_id):
        pass


# 0x842453b97eb8742178d6af105bdb5bb9340c058e8a6a1d0aedba5f73f15424e80a1da8896cbe9eac968ee75c89a4d5238fb83e501b527e1956f51c81d94e247301
# ["0xca35b7d915458ef540ade6068dfe2f44e8fa733c","0x14723a09acff6d2a60dcdf7aa4aff308fddc160c"],["0","0"],"0x19457468657265756d205369676e6564204d6573736167653a0a33313233","0x842453b97eb8742178d6af105bdb5bb9340c058e8a6a1d0aedba5f73f15424e80a1da8896cbe9eac968ee75c89a4d5238fb83e501b527e1956f51c81d94e247301","0x21dfbe1c391b2ff861cb3163e70bf1b4c80b61f77f91cbe198967917cd9a22d5","1"
