
# python modules
from random import randint
import rlp
import logging.handlers
import json

# ethereum modules
from hexbytes import HexBytes
from eth_hash.auto import keccak

# uip modules
from uiputils.op_intents import OpIntents
from uiputils.transaction import StateType
from uiputils.transaction_intents import TransactionIntents
from uiputils.chain_dns import ChainDNS
from uiputils.isc import InsuranceSmartContract
from uiputils.errors import Missing, Mismatch, VerificationError
from uiputils.uiptypes import Attestation

# eth modules
from uiputils.ethtools import JsonRPC, SignatureVerifier
from uiputils.nsb import EthLightNetStatusBlockChain

# config
from uiputils.config import HTTP_HEADER, INCLUDE_PATH, ves_log_dir

# constant
ENC = 'utf-8'


class VerifiableExecutionSystem:
    # the ves in uip

    class VesLog:
        formatter = logging.Formatter('%(asctime)-15s %(name)s %(vesaddr)-8s %(message)s')
        logger = logging.getLogger('ves')
        logger.setLevel(logging.INFO)
        handle = logging.handlers.TimedRotatingFileHandler(
            ves_log_dir,
            encoding="utf-8",
            when="H",
            interval=1,
            backupCount=10
        )
        handle.setFormatter(formatter)
        handle.setLevel(logging.INFO)
        handle.suffix = "%Y-%m-%d_%H.log"
        logger.addHandler(handle)

    INVALID = 0
    INITIAL_SESSION = {
        'tx_intents': None,
        'isc_addr': None,
        'Atte': {},
        'Merk': {},
        'ack_dict': {},
        'ack_counter': 0,
        'users': None
    }

    def __init__(self):
        # TODO: temporary eth-address
        self.address = "0x4f984aa7d262372df92f85af9be8d2df09ac4018"
        self.password = "123456"
        self.chain_host = "http://127.0.0.1:8545"
        self.domain = "Ethereum://Chain1"
        ###########################################################

        # TODO: temporary eth-nsb-address
        self.nsb = EthLightNetStatusBlockChain(
            self.address,
            self.chain_host,
            "0x4f358c8e9b891082eb61fb96f1a0cbdf23c14b6b"
        )
        ###########################################################

        self.txs_pool = {
            VerifiableExecutionSystem.INVALID: VerifiableExecutionSystem.INITIAL_SESSION
        }
        self.isc = InsuranceSmartContract
        self.user_pool = {}
        pass

    # async receiveIntents(self, intents):
    #     pass

    # async receiveTransactions(self, txs):
    #     pass

    def session_setup_prepare(self, op_intents_json):
        session_id = 0
        while session_id in self.txs_pool:
            session_id = randint(0, 0xffffffff)

        # TODO: test by stable sid
        session_id = 1

        self.info("sessionSetupPrepare {sid}".format(sid=session_id))

        # pre-register
        self.txs_pool[session_id] = VerifiableExecutionSystem.INITIAL_SESSION

        # create txs
        tx_intents, op_owners = VerifiableExecutionSystem.build_graph(op_intents_json)

        from uiputils.uiptools.cast import formated_json
        print(formated_json(tx_intents.dictize()))

        # check owners
        wait_user = set()
        for owner in op_owners:
            owner_name, host_name = [split_str[::-1] for split_str in owner[::-1].split('.', 1)]
            if owner_name not in self.user_pool:
                self.debug("session-id: {sid} setupPrepareError {exec}".format(
                    sid=session_id,
                    exec=Missing(owner_name + " is not in user-pool").error_info
                ))
                raise Missing(owner_name + " is not in user-pool")
            wait_user.add(self.domain + '.' + owner_name)
            owner_dapp = self.user_pool[owner_name]
            if host_name not in owner_dapp.info:
                self.debug("session-id: {sid} setupPrepareError {exec}".format(
                    sid=session_id,
                    exec=Missing(owner_name + " has no account on chain " + host_name).error_info
                ))
                raise Missing(owner_name + " has no account on chain " + host_name)

        # sign tx_intent
        sign_content = [str(session_id), tx_intents.purejson()]
        sign_bytes = HexBytes(rlp.encode(sign_content)).hex()
        atte_v = self.sign(sign_bytes)

        # build isc
        try:
            isc = InsuranceSmartContract(
                [self.address] + ChainDNS.gatherusers(op_owners, userformat='dot-concated'),
                ves=self,
                tx_head={'from': self.address, 'gas': hex(400000)},
                # rlped_txs=sign_bytes,
                # signature=atte_v,
                # tx_count=len(tx_intents.intents)
                # test by deployed contract
                contract_addr="0x83aed2040883c7e91a7792c5b62321e6c0741252"
            )
        except Exception as e:
            self.debug('session-id: {sid} ISCBulidError: {exec}'.format(
                sid=session_id,
                exec=str(e)
            ))
            raise e
        self.info("session-id: {sid} ISC bulit at {isc_addr}".format(
            sid=session_id,
            isc_addr=isc.address
        ))

        # update isc's information
        for idx, tx_intent in enumerate(tx_intents.intents):
            print(idx, tx_intent.jsonize())
            # intent_json = dict(tx_intent.jsonize())
            # fr: str
            # to: str
            # amt: str
            # if 'from' in intent_json:
            #     fr = intent_json['from']
            # if 'to' in intent_json:
            #     to = intent_json['to']
            # if 'value' in intent_json:
            #     amt = int(intent_json['value'], 16)
            # self.unlockself()
            # update_lazyfunc = isc.handle.update_tx_info(
            #     idx,
            #     fr=fr,
            #     to=to,
            #     seq=idx,
            #     amt=amt,
            #     meta=tx_intent.__dict__,
            #     lazy=True
            # )
            # print(update_lazyfunc, type(update_lazyfunc))
            # self.unlockself()
            # update_lazyfunc.transact()
            # update_resp = update_lazyfunc.loop_and_wait()
            # print(update_resp['transactionHash'])
            # self.unlockself()
            # print(isc.handle.get_transaction_info(idx))
            #
            # self.unlockself()
            # print(isc.handle.freeze_info(idx))
            # TODO: check isc-info updated

        # undate session information
        session_info = self.txs_pool[session_id]
        session_info['tx_intents'] = tx_intents
        session_info['ack_dict'] = dict((owner, None) for owner in wait_user)
        session_info['ack_counter'] = len(wait_user)
        session_info['ack_dict']['self_first'] = atte_v
        session_info['isc_addr'] = isc.address

        # TODO: async - send tx_intents
        return sign_content, isc, atte_v, tx_intents

    def session_setup_update(self, session_id, ack_user_name, ack_signature):
        if session_id not in self.txs_pool:
            return KeyError("session (id=" + str(session_id) + ") is not valid anymore")

        if ack_user_name not in self.txs_pool[session_id]['ack_dict']:
            return Missing('You have no right to vote on this session')

        if ack_signature is None:
            self.txs_pool.pop(session_id)
            self.info("session-id: {sid} aborted".format(sid=session_id))
            # TODO: inform Aborted

        print(ack_user_name, ChainDNS.get_user(ack_user_name))

        if self.txs_pool[session_id]['ack_dict'][ack_user_name] is None:
            if not SignatureVerifier.verify_by_raw_message(
                ack_signature,
                HexBytes(self.txs_pool[session_id]['ack_dict']['self_first']),
                ChainDNS.get_user(ack_user_name)
            ):
                return Mismatch('invalid signature')
            self.txs_pool[session_id]['ack_counter'] -= 1
            self.txs_pool[session_id]['ack_dict'][ack_user_name] = ack_signature
            self.info("session-id: {sid} user-ack: {ack_name} {ack_sig}".format(
                sid=session_id,
                ack_name=ack_user_name,
                ack_sig=ack_signature
            ))

        if self.txs_pool[session_id]['ack_counter'] == 0:
            self.session_setup_finish(session_id)

    def session_setup_finish(self, session_id):
        self.info("session-id: {sid} setup finished".format(
            sid=session_id
        ))

        session_info = self.txs_pool[session_id]

        # TODO: await isc-State == opening

        # TODO: Send Request(Tx-intents) NSB
        lazy_func = self.nsb.add_transaction_proposal(
            session_info['isc_addr'],
            len(session_info['tx_intents'].intents)
        )
        self.unlockself()
        lazy_func.transact()
        if lazy_func.loop_and_wait():
            self.info("session-id: {sid} add NSB's info success: ISC-address: {isc_addr}, Intents-count: {tx_count}".format(
                sid=session_id,
                isc_addr=session_info['isc_addr'],
                tx_count=len(session_info['tx_intents'].intents)
            ))
        else:
            self.info("session-id: {sid} add NSB's info failed: ISC-address: {isc_addr}, Intents-count: {tx_count}".format(
                sid=session_id,
                isc_addr=session_info['isc_addr'],
                tx_count=len(session_info['tx_intents'].intents)
            ))

    @staticmethod
    def build_graph(op_intents_json):
        # build eligible Op intents
        op_intents, op_owners = OpIntents.createopintents(op_intents_json['Op-intents'])

        # Generate Transaction intents and Dependency Graph
        # TODO:sort Graph
        return TransactionIntents(op_intents, op_intents_json['dependencies']), op_owners

    def send_txinfo_to_nsb(self, info):
        pass

    def unlockself(self):
        unlock = JsonRPC.personal_unlock_account(self.address, self.password, 20)
        response = JsonRPC.send(unlock, HTTP_HEADER, self.chain_host)
        if not response['result']:
            raise ValueError("unlock failed. wrong password?")

    def sign(self, msg):
        self.unlockself()
        sign_json = JsonRPC.eth_sign(self.address, msg)
        return JsonRPC.send(sign_json, HTTP_HEADER, self.chain_host)['result']

    def watching(self, session_id):
        pass

    def add_attestation(self, session_id, atte):
        pass

    def add_merkleproof(self, session_id, merk):
        pass

    # tmp function
    def appenduserlink(self, users):
        if isinstance(users, list):
            for user in users:
                self.appenduserlink(user)
        else:  # assuming be class dApp
            self.user_pool[users.name] = users

    def receive(self, rlped_atte):
        try:
            # TODO: verify attestation is on the nsb
            atte = Attestation(rlped_atte)
        except VerificationError as e:
            # TODO: stop ISC ?
            raise e

        return atte

    def sign_attestation(self, atte: Attestation):
        return atte.sign_and_encode([
            self.sign(HexBytes(atte.hash()).hex()),
            self.address
        ])

    def init_attestation(self, onchain_tx: dict, state: StateType, session_index: int, tx_index: int):
        content_list = [
            json.dumps(
                onchain_tx,
                sort_keys=True
            ).encode(ENC),
            HexBytes(state.value),
            HexBytes(session_index),
            HexBytes(tx_index)
        ]
        return Attestation.create_attestation(
            content_list,
            [
                self.sign(HexBytes(keccak(rlp.encode([content_list, []]))).hex()),
                self.address
            ]
        )

    def debug(self, msg):
        VerifiableExecutionSystem.VesLog.logger.debug(msg, extra={'vesaddr': self.address})

    def info(self, msg):
        VerifiableExecutionSystem.VesLog.logger.info(msg, extra={'vesaddr': self.address})
