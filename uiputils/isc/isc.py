

from functools import partial
import time

from eth_hash.auto import keccak
from eth_utils import to_checksum_address, to_normalized_address, to_canonical_address
from hexbytes import HexBytes
from web3 import Web3

from uiputils.uiptools.cast import JsonRlpize
from uiputils.contract.eth_contract import EthContract
from uiputils.ethtools import AbiEncoder, FileLoad, JsonRPC
from uiputils.transaction import StateType
from uiputils.uiptypes import Attestation
from uiputils.errors import Missing

from uiputils.config import isc_log_dir, isc_abi_dir, isc_bin_dir, ETHSIGN_HEADER
from uiputils.loggers import console_logger, AddressFileLogger

from abc import abstractmethod, ABCMeta


# constant
ENC = 'utf-8'

# global
isc_log = AddressFileLogger('isc', isc_log_dir)


class InsuranceSmartContract(object, metaclass=ABCMeta):
    """
    Insurance Smart Contract is a contract on the blockchain
    """

    def __init__(self):
        self.address = ""
        self.tx_header: dict = {}

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, addr):
        if addr == "" or addr == b"":
            self._address = ""
        else:
            self._address = to_checksum_address(addr)

    @property
    def checksum_address(self):
        return self._address

    @property
    def normalized_address(self):
        return to_normalized_address(self._address)

    @property
    def canonical_address(self):
        return  to_canonical_address(self._address)

    @property
    def tx_header(self):
        return self._tx_header

    @tx_header.setter
    def tx_header(self, tx):
        self._tx_header = dict(tx)
        if self._tx_header is not None:
            if 'from' in self._tx_header:
                self._tx_header['from'] = to_checksum_address(self._tx_header['from'])
            if 'to' in self._tx_header:
                self._tx_header['to'] = to_checksum_address(self._tx_header['to'])

    @abstractmethod
    def insurance_claim(self, atte: Attestation, tid, state, nsb_addr, result=None, tcg=None, tx=None):
        """
        insurance claim
        """

    @abstractmethod
    def settle_contract(self):
        """
        settle contract
        """

    def return_funds(self, tx=None):
        """
        return funds
        """

    @staticmethod
    def make_contract(*args, **kwargs):
        """
        make contract
        """


class EthInsuranceSmartContract(InsuranceSmartContract):
    """
    implemented Insurance Smart Contract on ethereum
    """

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
        contract_addr=None,
        isc_bytecode_dir=None
    ):
        super().__init__()
        self.debugger = partial(isc_log.debug, extra={'iscaddr': self.address})
        self.infoer = partial(isc_log.info, extra={'iscaddr': self.address})
        if contract_addr is None:
            if rlped_txs is None or signature is None or owners is None or ves is None or tx_count is None:
                pass
            else:
                self.address = EthInsuranceSmartContract.make_contract(
                    owners=owners,
                    signature=signature,
                    rlped_txs=rlped_txs,
                    tx_count=tx_count,
                    ves=ves,
                    bin_dir=bin_dir
                )
                self.debugger('NewISCBuilt owners: {owners}'.format(owners=owners))
        else:
            self.address = contract_addr
        self.owners = owners
        self.handle = EthContract(
            ves.chain_host, Web3.toChecksumAddress(self.address), abi_dir, isc_bytecode_dir
        )
        console_logger.info('isc {} built'.format(self.address))

        self.web3 = self.handle.web3
        self.tx = tx_head.copy()

        console_logger.info('isc({0}) init: functions:{1}'.format(self.address, self.handle.funcs()))

    @staticmethod
    def make_contract(owners, signature, rlped_txs, tx_count, ves, bytescode=None, bin_dir=isc_bin_dir):
        try:
            rlped_txs = HexBytes(rlped_txs)
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
            if bytescode is None:
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
            isc_log.debug('ISCBulidError: {}'.format(str(e)))
            raise e
        while True:
            try:

                response = JsonRPC.send(rp_json, rpc_host=ves.chain_host)
                if response['result'] is None:
                    console_logger.info("Contract is deploying, please stand by")
                    time.sleep(2)
                    continue
                console_logger.info("got Transaction_result {}".format(response['result']))

                block_number = response['result']['blockNumber']
                contract_addr = response['result']['contractAddress']

                cd_json = JsonRPC.eth_get_code(contract_addr, block_number)
                response = JsonRPC.send(cd_json, rpc_host=ves.chain_host)
                if response['result'] == '0x':
                    raise IndexError("Contract deployment failed")

                return contract_addr
            except Exception as e:
                isc_log.debug('ISCBulidError: {exec}'.format(exec=str(e)), extra={"addr": ""})
                raise e

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
        if isinstance(meta, dict):
            meta = JsonRlpize.serialize(meta)
        elif not isinstance(meta, str) and not isinstance(meta, bytes):
            raise ValueError("unexpected meta-type" + str(type(meta)))
        if lazy:
            return self.handle.lazyfunct(
                'updateTxInfo',
                tx, idx,
                Web3.toChecksumAddress(fr),
                Web3.toChecksumAddress(to),
                seq, amt, meta,
            )
        else:
            return self.handle.funct(
                'updateTxInfo',
                tx, idx,
                Web3.toChecksumAddress(fr),
                Web3.toChecksumAddress(to),
                seq, amt, meta, timeout=timeout
            )

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

    def insurance_claim(self, atte: Attestation, tid, state, nsb_addr, result=None, tcg=None, tx=None):
        if tx is None:
            tx = self.tx
        console_logger.info('isc({0}) claiming:\n Attestation: {1},\n tid:{2},\n state: {3}'.format(
            self.address, atte.__dict__, tid, state
        ))
        print(atte, "is not verified")
        if state == StateType.opened:
            if tcg is None:
                raise Missing("the opening time of Transaction must be given")
            return self.handle.funct('ChangeStateOpened', tx, tid, tcg)
        elif state == StateType.closed:
            if tcg is None:
                raise Missing("the close time of Transaction must be given")
            return self.handle.funct('ChangeStateClosed', tx, tid, tcg)
        elif state == StateType.open:
            if result is None:
                raise Missing("the result of Transaction must be given")
            return (
                self.handle.funct('ChangeState', tx, tid, state),
                self.handle.funct('ChangeResult', tx, nsb_addr, tid, result)
            )
        else:
            return self.handle.funct('ChangeState', tx, tid, state)

    def stop_isc(self, tx=None):
        if tx is None:
            tx = self.tx
        console_logger.info('isc({}) closed'.format(self.address))
        return self.handle.funct('StopISC', tx)

    def settle_contract(self, tx=None):
        if tx is None:
            tx = self.tx
        console_logger.info('isc({}) settling'.format(self.address))
        return self.handle.funct('settleContract', tx)

    def update_funds(self, owner, tx):
        if owner not in self.owners:
            raise Missing('this address is not owner')
        console_logger.info('isc({}) updating funds'.format(self.address))
        print(owner, "updated fund:", tx)

    def return_funds(self, tx=None):
        if tx is None:
            tx = self.tx
        console_logger.info('isc({}) returing funds'.format(self.address))
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
        console_logger.info('geted transaction information(index: {0}) {1}'.format(tid, ret))
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


# isc test parameters
# ["0xca35b7d915458ef540ade6068dfe2f44e8fa733c","0x14723a09acff6d2a60dcdf7aa4aff308fddc160c"],
# ["0","0"],"0x19457468657265756d205369676e6564204d6573736167653a0a33313233",
# "0x842453b97eb8742178d6af105bdb5bb9340c058e8a6a1d0aedba5f73f15424e8
#  0a1da8896cbe9eac968ee75c89a4d5238fb83e501b527e1956f51c81d94e247301",
# "0x21dfbe1c391b2ff861cb3163e70bf1b4c80b61f77f91cbe198967917cd9a22d5","1"

# aborted codes ########################################################################################################

# eth __init__:
# self.updateFunc = {
#     'fr': partial(self.handle.funct, funcname='updateTxFr'),
#     'to': partial(self.handle.funct, funcname='updateTxTo'),
#     'seq': partial(self.handle.funct, funcname='updateTxSeq'),
#     'amt': partial(self.handle.funct, funcname='updateTxAmt'),
#     'rlped_data': partial(self.handle.funct, funcname='updateTxRlpedData')
# }

# eth make contract:
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

# eth update info:
# if spec is None:
#     ...
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
