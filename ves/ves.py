
# python modules
from random import randint
import rlp
import logging.handlers
import json

# ethereum modules
from hexbytes import HexBytes
from eth_hash.auto import keccak

# uip modules
from uiputils.op_intents import OpIntent
from uiputils.transaction import StateType
from uiputils.transaction_intents import TransactionIntents
from uiputils.chain_dns import ChainDNS
import isc as isc_module
from isc import TenInsuranceSmartContract as InsuranceSmartContract
from uiputils.errors import Missing, VerificationError
from uiputils.uiptypes import Attestation
from uiputils.contract.wrapped_contract_function import ContractFunctionClient

# eth modules
from uiputils.ethtools import JsonRPC

# nsb modules
from py_nsbcli import Client

from py_nsbcli.system_action import SystemAction, Action

# config
from uiputils.config import HTTP_HEADER, ves_log_dir, action_using_flag, alice
from uiputils.loggers import  console_logger

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
        'ack_dict': {},
        'ack_counter': 0,
        'users': None
    }

    def __init__(self):
        # TODO: temporary eth-address
        self.address = "0xf4dacff5eba7426295e27a32d389fff3cde55de2"
        self.password = "123456"
        self.chain_host = "http://162.105.87.118:8545"
        self.domain = "Ethereum://chain3"
        ###########################################################

        self.nsb = Client("http://47.254.66.11:26657")
        # TODO: temporary eth-nsb-address
        # self.nsb = EthLightNetStatusBlockChain(
        #     self.address,
        #     self.chain_host,
        #     "0x15055c5173c91957ea49552bdee55487e3c2ac43"
        # )
        ###########################################################

        self.txs_pool = {
            VerifiableExecutionSystem.INVALID: VerifiableExecutionSystem.INITIAL_SESSION
        }
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
        console_logger.info("sessionSetupPrepare {sid}".format(sid=session_id))

        # pre-register
        self.txs_pool[session_id] = dict(VerifiableExecutionSystem.INITIAL_SESSION)

        # create txs
        tx_intents, op_owners = VerifiableExecutionSystem.build_graph(op_intents_json)

        from uiputils.uiptools.cast import formated_json
        console_logger.info('ves-session[{0}]  init tx_intents: {1}'.format(
            session_id, formated_json(tx_intents.dictize())
        ))
        console_logger.info('ves-session[{0}]  init op_owners: {1}'.format(session_id, op_owners))

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
            wait_user.add("Tendermint://chain1" + '.' + owner_name)
            owner_dapp = self.user_pool[owner_name]
            if host_name not in owner_dapp.info:
                self.debug("session-id: {sid} setupPrepareError {exec}".format(
                    sid=session_id,
                    exec=Missing(owner_name + " has no account on chain " + host_name).error_info
                ))
                raise Missing(owner_name + " has no account on chain " + host_name)

        console_logger.info('ves-session[{0}] init wait_owners: {1}'.format(session_id, wait_user))

        # sign tx_intent
        sign_content = [str(session_id), tx_intents.purejson()]
        sign_bytes = HexBytes(rlp.encode(sign_content)).hex()
        atte_v = self.sign(sign_bytes)

        console_logger.info('ves-session[{0}] init wait_owners: {1}'.format(session_id, wait_user))

        # build isc
        try:
            isc = InsuranceSmartContract(
                isc_owners=[self.address] + ChainDNS.gatherusers(wait_user, userformat='dot-concated'),
                transaction_intents=tx_intents,
                required_funds=[0, 0, 0],
                ves_signature=atte_v,
                host_addr=self.nsb.host
                # test by deployed contract
                # contract_addr="0x0C24884AEe4E89378Bb1E739A5c9b34834D384E5"
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

        console_logger.info('ves-session[{0}] created isc: address on {1}\n owner {2} '.format(
            session_id, isc.address, isc.owners
        ))

        # update isc's information
        self.send_txinfo_to_isc(isc, tx_intents, testing=False)

        # update session information
        session_info = self.txs_pool[session_id]
        session_info['tx_intents'] = tx_intents
        session_info['ack_dict'] = dict((owner, None) for owner in wait_user)
        session_info['ack_counter'] = len(wait_user)
        session_info['ack_dict']['self_first'] = atte_v
        session_info['isc_addr'] = isc.address

        console_logger.info('session_info[{0}] updated {1}'.format(session_id, session_info))

        # TODO: async - send tx_intents
        return sign_content, isc, atte_v, tx_intents

    def session_setup_update(self, session_id, ack_user_name, ack_signature):
        if session_id not in self.txs_pool:
            return KeyError("session (id=" + str(session_id) + ") is not valid anymore")
        # print("ac", ack_user_name)
        if ack_user_name not in self.txs_pool[session_id]['ack_dict']:
            return Missing('You have no right to vote on this session')

        if ack_signature is None:
            self.txs_pool.pop(session_id)
            self.info("session-id: {sid} aborted".format(sid=session_id))
            # TODO: inform Aborted

        if self.txs_pool[session_id]['ack_dict'][ack_user_name] is None:
            # if not SignatureVerifier.verify_by_raw_message(
            #     ack_signature,
            #     HexBytes(self.txs_pool[session_id]['ack_dict']['self_first']),
            #     ChainDNS.get_user(ack_user_name)
            # ):
            #     return Mismatch('invalid signature')
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

        # TODO: await isc-State == opening

        # TODO: Send Request(Tx-intents) NSB

        self.send_txinfo_to_nsb(session_id, testing=False)

    @staticmethod
    def build_graph(op_intents_json):
        # build eligible Op intents
        op_intents, op_owners = OpIntent.createopintents(op_intents_json['Op-intents'])

        # Generate Transaction intents and Dependency Graph
        # TODO:sort Graph
        return TransactionIntents(op_intents, op_intents_json['dependencies']), op_owners

    def send_txinfo_to_nsb(self, session_id, testing=False):
        if isinstance(self.nsb, Client):
            return
        if testing:
            return
        session_info = self.txs_pool[session_id]
        console_logger.info('ves adding isc({0}) with size of transactions: {1}'.format(
            session_info['isc_addr'], len(session_info['tx_intents'].intents)
        ))
        lazy_func = self.nsb.add_transaction_proposal(
            session_info['isc_addr'],
            len(session_info['tx_intents'].intents)
        )
        self.unlockself()
        lazy_func.transact()
        resp = lazy_func.loop_and_wait()
        console_logger.info('nsb response of adding isc({0}): {1}'.format(session_info['isc_addr'], resp))
        if resp:
            self.info(
                "session-id: {sid} add NSB's info success: ISC-address: {isc_addr}, Intents-count: {tx_count}".format(
                    sid=session_id,
                    isc_addr=session_info['isc_addr'],
                    tx_count=len(session_info['tx_intents'].intents)
                )
            )
        else:
            self.info(
                "session-id: {sid} add NSB's info failed: ISC-address: {isc_addr}, Intents-count: {tx_count}".format(
                    sid=session_id,
                    isc_addr=session_info['isc_addr'],
                    tx_count=len(session_info['tx_intents'].intents)
                )
            )

    def send_txinfo_to_isc(self, isc, tx_intents, testing=False):
        if isinstance(isc, isc_module.TenInsuranceSmartContract):
            return

        if testing:
            return
        for idx, tx_intent in enumerate(tx_intents.intents):
            console_logger.info('updating tx_info(index: {0}): {1}'.format(idx, tx_intent.jsonize()))
            intent_json = dict(tx_intent.jsonize())

            fr = "0x0000000000000000000000000000000000000000"
            to = "0x0000000000000000000000000000000000000000"
            amt = 0
            if 'from' in intent_json:
                fr = intent_json['from']
            if 'to' in intent_json:
                to = intent_json['to']
            if 'value' in intent_json:
                amt = int(intent_json['value'], 16)

            update_lazyfunc = isc.update_tx_info(
                idx,
                fr=fr,
                to=to,
                seq=idx,
                amt=amt,
                meta=tx_intent.__dict__,
                lazy=True
            )
            self.unlockself()
            update_lazyfunc.transact()

            update_resp = update_lazyfunc.loop_and_wait()
            console_logger.info('update response: {0}'.format(update_resp))

            self.unlockself()
            console_logger.info(
                'isc({0})updated information(index: {1}): {2}'.format(
                    isc.address, idx, isc.get_transaction_info(idx)
                )
            )

            self.unlockself()
            console_logger.info(
                'freeze_info response: {}'.format(isc.freeze_info(idx))
            )
            # TODO: check isc-info updated

    def unlockself(self, hostname=None):
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

    def receive(self, rlped_atte, session_id, tid, aid, host_name=None):
        try:
            if session_id not in self.txs_pool:
                raise KeyError("No such session_id" + str(session_id))

            # session_info = self.session_event[session_id]
            # nsb = EthLightNetStatusBlockChain(
            #     session_info['host_info']['address'],
            #     session_info['host_info']['host'],
            #     session_info['nsb']
            # )
            sys_act = SystemAction(self.nsb.host)

            atte = Attestation(rlped_atte)
            print(sys_act.get_action(alice, bytes.fromhex("123456"), tid, aid))

        except VerificationError as e:
            # TODO: stop ISC ?
            raise e

        return atte

    def sign_attestation(self, atte: Attestation):
        return atte.sign_and_encode([
            self.sign(HexBytes(atte.hash).hex()),
            self.address
        ])

    def init_attestation(self, onchain_tx: dict, state: StateType, session_index: int, tx_index: int, host_name=None):
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

    def send_attestation(
            self,
            session_index: int,
            atte: Attestation,
            tx_index, state: StateType,
            host_name=None
    ) -> ContractFunctionClient:

        console_logger.info(
            'ves ({0}) adding atte[\n'
            '     isc: {1}\n'
            '    transaction-action index: ({2}, {3})\n'
            '    atte: ({4}, {5})\n'
            ']'.format(
                self.address, self.txs_pool[session_index]['isc_addr'], tx_index, state.value,
                HexBytes(atte.pre_hash).hex(), atte.signatures[-1][0].to_hex()
            )
        )

        sys_act = SystemAction(self.nsb.host)
        sys_act.add_action(alice, Action(
            bytes.fromhex("123456"), tx_index, state.value,
            action_using_flag["Tendermint"].value, HexBytes(atte.pre_hash),
            atte.signatures[-1][0].bytes()
        ))

        # return self.nsb.add_action_proposal(
        #     self.txs_pool[session_index]['isc_addr'],
        #     tx_index,
        #     state.value,
        #     atte.pre_hash,
        #     atte.signatures[-1][0].to_hex()
        # )

    def debug(self, msg):
        VerifiableExecutionSystem.VesLog.logger.debug(msg, extra={'vesaddr': self.address})

    def info(self, msg):
        VerifiableExecutionSystem.VesLog.logger.info(msg, extra={'vesaddr': self.address})
