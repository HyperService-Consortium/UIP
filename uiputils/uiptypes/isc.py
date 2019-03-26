
import rlp
import time
import logging
import logging.handlers

from hexbytes import HexBytes
from eth_hash.auto import keccak

# uip modules
from uiputils.uiperror import Missing

from uiputils.eth.tools import AbiEncoder
from uiputils.eth.tools import FileLoad, JsonRPC
from uiputils.eth.ethtypes import EthInsuranceSmartContract as ethISC

from uiputils.config import ETHSIGN_HEADER, isc_log_dir
ENC = 'utf-8'


class InsuranceSmartContract:
    class ISCLog:
        formatter = logging.Formatter('%(asctime)-15s %(name)s %(iscaddr)-8s %(message)s')
        logger = logging.getLogger('isc')
        logger.setLevel(logging.INFO)
        handle = logging.handlers.TimedRotatingFileHandler(
            isc_log_dir,
            encoding="utf-8",
            when="H",
            interval=1,
            backupCount=10
        )
        handle.setFormatter(formatter)
        handle.setLevel(logging.INFO)
        handle.suffix = "%Y-%m-%d_%H_%M.log"
        logger.addHandler(handle)

    def __init__(
        self,
        owners,
        abi_dir,
        rlped_txs=None,
        signature=None,
        ves=None,
        tx_head=None,
        tx_count=None,
        contract_addr=None
    ):
        # Insurance Smart Contract is a contract on the blockchain
        # TODO : contract construct
        if contract_addr is None:
            if rlped_txs is None or signature is None or owners is None or ves is None:
                self.address = None
            else:
                try:
                    rlped_txs = HexBytes(rlped_txs)
                    # print(
                    #     owners, ',',
                    #     [0, 0, 0], ',',
                    #     HexBytes(ETHSIGN_HEADER + bytes(str(len(rlped_txs)).encode(ENC)) + bytes(rlped_txs)).hex(), ',',
                    #     signature, ',',
                    #     HexBytes(keccak(ETHSIGN_HEADER + b'\x31\x33\x30' + bytes(signature[2:].encode(ENC)))).hex(), ',',
                    #     3
                    # )
                    encoded_data = AbiEncoder.encodes(
                        [
                            owners,
                            [0, 0, 0],
                            HexBytes(ETHSIGN_HEADER + bytes(str(len(rlped_txs)).encode(ENC)) + bytes(rlped_txs)).hex(),
                            signature,
                            keccak(ETHSIGN_HEADER + b'\x31\x33\x30' + bytes(signature[2:].encode(ENC))),
                            tx_count
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
                    rp_json = JsonRPC.eth_get_transaction_receipt(response['result'])
                except Exception as e:
                    self.debug('ISCBulidError: {exec}'.format(
                        exec=str(e)
                    ))
                    raise e
                while True:
                    try:
                        response = JsonRPC.send(rp_json, rpc_host=ves.chain_host)
                        if response['result'] is None:
                            print("Contract is deploying, please stand by")
                            time.sleep(2)
                            continue
                        print("got Transaction_result", response['result'])
                        block_number = response['result']['blockNumber']
                        contract_addr = response['result']['contractAddress']
                        cd_json = JsonRPC.eth_get_code(contract_addr, block_number)
                        response = JsonRPC.send(cd_json, rpc_host=ves.chain_host)

                        # print(code_resp)
                        if response['result'] == '0x':
                            raise IndexError("Contract deployment failed")
                        self.address = contract_addr
                        break
                    except Exception as e:
                        self.debug('ISCBulidError: {exec}'.format(
                            exec=str(e)
                        ))
                        raise e
                self.info('NewISCBuilt owners: {owners}'.format(
                    owners=owners
                ))
        else:
            self.address = contract_addr
        self.owners = owners
        self.handle = ethISC(ves.chain_host, self.address, abi_dir, tx_head)
        print(self.address)

    def update_TxInfo(self, tx):
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

    def debug(self, msg):
        InsuranceSmartContract.ISCLog.logger.debug(msg, extra={'iscaddr': self.address})

    def info(self, msg):
        InsuranceSmartContract.ISCLog.logger.info(msg, extra={'iscaddr': self.address})


# 0x842453b97eb8742178d6af105bdb5bb9340c058e8a6a1d0aedba5f73f15424e80a1da8896cbe9eac968ee75c89a4d5238fb83e501b527e1956f51c81d94e247301
# ["0xca35b7d915458ef540ade6068dfe2f44e8fa733c","0x14723a09acff6d2a60dcdf7aa4aff308fddc160c"],["0","0"],"0x19457468657265756d205369676e6564204d6573736167653a0a33313233","0x842453b97eb8742178d6af105bdb5bb9340c058e8a6a1d0aedba5f73f15424e80a1da8896cbe9eac968ee75c89a4d5238fb83e501b527e1956f51c81d94e247301","0x21dfbe1c391b2ff861cb3163e70bf1b4c80b61f77f91cbe198967917cd9a22d5","1"
