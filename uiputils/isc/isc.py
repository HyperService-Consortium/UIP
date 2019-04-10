import logging.handlers
import time

from eth_hash.auto import keccak
from hexbytes import HexBytes
from web3 import Web3

from uiputils.uiptools.cast import JsonRlpize
from uiputils.contract.eth_contract import EthContract
from uiputils.ethtools import AbiEncoder, FileLoad, JsonRPC
from uiputils.transaction import StateType
from uiputils.errors import Missing

from uiputils.config import isc_log_dir, isc_abi_dir, isc_bin_dir, ETHSIGN_HEADER

# constant
ENC = 'utf-8'


class EthInsuranceSmartContract:

    def __init__(self, host, isc_addr, isc_abi_dir, tx=None, isc_bytecode_dir=None):
        self.handle = EthContract(host, Web3.toChecksumAddress(isc_addr), isc_abi_dir, isc_bytecode_dir)
        self.web3 = self.handle.web3
        self.address = self.handle.address
        self.tx = tx.copy()
        if self.tx is not None:
            if 'gas' in self.tx:
                self.tx.pop('gas')
            if 'from' in self.tx:
                self.tx['from'] = Web3.toChecksumAddress(self.tx['from'])
        # self.updateFunc = {
        #     'fr': partial(self.handle.funct, funcname='updateTxFr'),
        #     'to': partial(self.handle.funct, funcname='updateTxTo'),
        #     'seq': partial(self.handle.funct, funcname='updateTxSeq'),
        #     'amt': partial(self.handle.funct, funcname='updateTxAmt'),
        #     'rlped_data': partial(self.handle.funct, funcname='updateTxRlpedData')
        # }
        print(self.handle.funcs())

    def update_tx_info(
            self,
            idx,
            fr=None,
            to=None,
            seq=None,
            amt=None,
            meta=None,
            tx: dict = None,
            # spec: set = None,
            lazy=False,
            timeout=10
    ):
        if tx is None:
            tx = self.tx
        # if spec is None:
        if isinstance(meta, dict):
            meta = JsonRlpize.serialize(meta)
        elif not isinstance(meta, str) and not isinstance(meta, bytes):
            raise ValueError("unexpected meta-type" + str(type(meta)))
        if lazy:
            return self.handle.lazyfunct(
                'updateTxInfo',
                tx,
                idx,
                Web3.toChecksumAddress(fr),
                Web3.toChecksumAddress(to),
                seq,
                amt,
                meta,
            )
        else:
            return self.handle.funct(
                'updateTxInfo',
                tx,
                idx,
                Web3.toChecksumAddress(fr),
                Web3.toChecksumAddress(to),
                seq,
                amt,
                meta,
                timeout=timeout
            )
        # else:
        #     if 'fr' in spec:
        #         self.handle.funct('updateTxFr', tx, Web3.toChecksumAddress(fr), timeout=timeout)
        #     if 'to' in spec:
        #         self.handle.funct('updateTxTo', tx, Web3.toChecksumAddress(to), timeout=timeout)
        #     if 'seq' in spec:
        #         self.handle.funct('updateTxSeq', tx, seq, timeout=timeout)
        #     if 'amt' in spec:
        #         self.handle.funct('updateTxAmt', tx, amt, timeout=timeout)
        #     if 'rlped_meta' in spec:
        #         self.handle.funct('updateTxRlpedMeta', tx, rlped_meta, timeout=timeout)
        #     # return tuple((self.updateFunc[spec_type](kwargs) for spec_type in spec))

    def user_stake(self, tx):
        return self.handle.funct('stakeFund', tx)

    def user_ack(self, sig, tx=None):
        if tx is None:
            tx = self.tx
        return self.handle.lazyfunct('userAck', tx, sig)

    def user_refuse(self, tx=None):
        if tx is None:
            tx = self.tx
        return self.handle.funct('userRefuse', tx)

    def insurance_claim(self, atte, tid, state, nsb=None, result=None, tcg=None, tx=None):
        if tx is None:
            tx = self.tx
        print(atte, "is not verified")
        if state == StateType.opened:
            return self.handle.funct('ChangeStateOpened', tx, tid, tcg)
        elif state == StateType.closed:
            return self.handle.funct('ChangeStateClosed', tx, tid, tcg)
        elif state == StateType.open:
            return (
                self.handle.funct('ChangeState', tx, tid, state),
                self.handle.funct('ChangeResult', tx, nsb, tid, result)
            )
        else:
            return self.handle.funct('ChangeState', tx, tid, state)

    def stop_isc(self, tx=None):
        if tx is None:
            tx = self.tx
        return self.handle.funct('StopISC', tx)

    def settle_contract(self, tx=None):
        if tx is None:
            tx = self.tx
        return self.handle.funct('settleContract', tx)

    def return_funds(self, tx=None):
        if tx is None:
            tx = self.tx
        return self.handle.funct('returnFunds', tx)

    def is_owner(self, addr):
        return self.handle.func('isOwner', Web3.toChecksumAddress(addr))

    def is_raw_sender(self, addr):
        return self.handle.func('isRawSender', Web3.toChecksumAddress(addr))

    def tx_info_length(self):
        return self.handle.func('txInfoLength')

    def get_meta_by_number(self, tid):
        return self.handle.func('getMetaByNumber', tid)

    def get_state(self, tid):
        return self.handle.func('getState', tid)

    def get_result(self, tid):
        return self.handle.func('getResult', tid)

    def get_transaction_info(self, tid):
        ret = self.handle.func('getTransactionInfo', tid)
        ret[4] = JsonRlpize.unserialize(ret[4])
        return ret

    def get_isc_state(self):
        return self.handle.func('iscState')

    def vesack(self):
        return self.handle.func('vesack')

    def freeze_info(self, idx, tx=None):
        if tx is None:
            tx = self.tx
        return self.handle.funct('freezeInfo', tx, idx)


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
        abi_dir=isc_abi_dir,
        bin_dir=isc_bin_dir,
        rlped_txs=None,
        signature=None,
        ves=None,
        tx_head=None,
        tx_count=None,
        contract_addr=None
    ):
        # Insurance Smart Contract is a contract on the blockchain
        self.address = ""
        if contract_addr is None:
            if rlped_txs is None or signature is None or owners is None or ves is None:
                pass
            else:
                try:
                    rlped_txs = HexBytes(rlped_txs)
                    # print(
                    #     owners, ',',
                    #     [0, 0, 0], ',',
                    #     HexBytes(
                    #         ETHSIGN_HEADER +
                    #         bytes(str(len(rlped_txs)).encode(ENC)) +
                    #         bytes(rlped_txs)
                    #     ).hex(), ',',
                    #     signature, ',',
                    #     HexBytes(keccak(
                    #         ETHSIGN_HEADER +
                    #         b'\x31\x33\x30' +
                    #         bytes(signature[2:].encode(ENC))
                    #     )).hex(), ',',
                    #     tx_count
                    # )
                    encoded_data = AbiEncoder.encodes(
                        [
                            owners,
                            [0, 0, 0],
                            HexBytes(ETHSIGN_HEADER + bytes(str(len(rlped_txs)).encode(ENC)) + bytes(rlped_txs)).hex(),
                            signature,
                            keccak(ETHSIGN_HEADER + b'\x36\x35' + HexBytes(signature)),
                            tx_count
                        ],
                        ['address[]', 'uint256[]', 'bytes', 'bytes', 'bytes32', 'uint256']
                    )
                    bytescode = FileLoad.getbytecode(bin_dir)
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
        self.handle = EthInsuranceSmartContract(ves.chain_host, self.address, abi_dir, tx_head)
        print(self.address)

    # def update_txinfo(self, tx):
    #     tx_info = tx.tx_info
    #     print(tx_info)

    def update_funds(self, owner, fund):
        if owner not in self.owners:
            raise Missing('this address is not owner')
        print(owner, "updated fund:", fund)

    def insurance_claim(self, atte):
        pass

    def settle_contract(self, contract_id):
        pass

    def debug(self, msg):
        InsuranceSmartContract.ISCLog.logger.debug(msg, extra={'iscaddr': self.address})

    def info(self, msg):
        InsuranceSmartContract.ISCLog.logger.info(msg, extra={'iscaddr': self.address})

# 0x842453b97eb8742178d6af105bdb5bb9340c058e8a6a1d0aedba5f73f15424e80a1da8896cbe9eac968ee75c89a4d5238fb83e501b527e1956f51c81d94e247301
# ["0xca35b7d915458ef540ade6068dfe2f44e8fa733c","0x14723a09acff6d2a60dcdf7aa4aff308fddc160c"],["0","0"],"0x19457468657265756d205369676e6564204d6573736167653a0a33313233","0x842453b97eb8742178d6af105bdb5bb9340c058e8a6a1d0aedba5f73f15424e80a1da8896cbe9eac968ee75c89a4d5238fb83e501b527e1956f51c81d94e247301","0x21dfbe1c391b2ff861cb3163e70bf1b4c80b61f77f91cbe198967917cd9a22d5","1"
