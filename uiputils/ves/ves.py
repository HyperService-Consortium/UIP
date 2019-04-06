
# python modules
from random import randint
import rlp
import logging.handlers

# ethereum modules
from hexbytes import HexBytes

# uip modules
from uiputils.op_intents import OpIntents
from uiputils.transaction_intents import TransactionIntents
from uiputils.chain_dns import ChainDNS
from uiputils.isc import InsuranceSmartContract
from uiputils.errors import Missing, Mismatch

# eth modules
from uiputils.ethtools import JsonRPC, SignatureVerifier

# config
from uiputils.config import HTTP_HEADER, INCLUDE_PATH, ves_log_dir


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
        'Atte': {},
        'Merk': {},
        'ack_dict': {},
        'ack_counter': 0,
        'users': None
    }

    def __init__(self):
        # temporary eth-address
        self.address = "0x4f984aa7d262372df92f85af9be8d2df09ac4018"
        self.password = "123456"
        self.chain_host = "http://127.0.0.1:8545"
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

        # test by stable sid
        session_id = 1

        self.info("sessionSetupPrepare {sid}".format(sid=session_id))

        # pre-register
        self.txs_pool[session_id] = VerifiableExecutionSystem.INITIAL_SESSION

        # create txs
        tx_intents, op_owners = VerifiableExecutionSystem.build_graph(op_intents_json)

        wait_user = set(op_owners)
        for owner in op_owners:
            if owner not in self.user_pool:
                self.debug("session-id: {sid} setupPrepareError {exec}".format(
                    sid=session_id,
                    exec=Missing(owner + " is not in user-pool").error_info
                ))
                raise Missing(owner + " is not in user-pool")

        # initalize ack_dict
        self.txs_pool[session_id]['ack_dict'] = dict((owner, None) for owner in wait_user)
        self.txs_pool[session_id]['ack_counter'] = len(wait_user)

        sign_content = [str(session_id), tx_intents.purejson()]
        sign_bytes = HexBytes(rlp.encode(sign_content)).hex()
        atte_v = self.sign(sign_bytes)
        self.txs_pool[session_id]['ack_dict']['self_first'] = atte_v

        isc: InsuranceSmartContract = None
        try:
            isc = InsuranceSmartContract(
                [self.address] + ChainDNS.gatherusers(op_owners, userformat='dot-concated'),
                INCLUDE_PATH + '/isc.abi',
                ves=self,
                tx_head={'from': self.address, 'gas': hex(400000)},
                rlped_txs=sign_bytes,
                signature=atte_v,
                tx_count=len(tx_intents.intents)
                # test by deployed contract
                # contract_addr="0x0092044dd5f294860d722a75d295cac378994409"
            )
        except Exception as e:
            self.debug('session-id: {sid} ISCBulidError: {exec}'.format(
                sid=session_id,
                exec=str(e)
            ))

        self.info("session-id: {sid} ISC bulit at {isc_addr}".format(
            sid=session_id,
            isc_addr=isc.address
        ))

        for idx, tx_intent in enumerate(tx_intents.intents):
            print(idx, tx_intent)
            pass
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
            # update_lazyfunc.transact()
            # update_resp = update_lazyfunc.loop_and_wait()
            # print(update_resp['transactionHash'])
            # self.unlockself()
            # print(isc.handle.get_transaction_info(idx))
            #
            # self.unlockself()
            # print(isc.handle.freeze_info(idx))
            # TODO: check isc-info updated

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

        if self.txs_pool[session_id]['ack_dict'][ack_user_name] is None:
            if not SignatureVerifier.verify_by_raw_message(
                ack_signature,
                HexBytes(self.txs_pool[session_id]['ack_dict']['self_first']),
                ChainDNS.adduser['dot-concated'](ack_user_name)
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
        # TODO: await isc-State == opening

        # TODO: Send Request(Tx-intents) NSB
        # nsb.add_transaction_proposal('0xb7eabab4d8deb73ebdc6c40c2c90db0c2e4160b4')
        pass

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

    def debug(self, msg):
        VerifiableExecutionSystem.VesLog.logger.debug(msg, extra={'vesaddr': self.address})

    def info(self, msg):
        VerifiableExecutionSystem.VesLog.logger.info(msg, extra={'vesaddr': self.address})
