
# python modules
from random import randint
import rlp

# ethereum modules
from hexbytes import HexBytes

# uip modules
from uiputils.uiptypes import InsuranceSmartContract, OpIntent, TransactionIntents, ChainDNS
from uiputils.eth import JsonRPC
from uiputils.eth.tools import SignatureVerifier
from uiputils.uiperror import Missing, Mismatch

# config
from uiputils.config import HTTP_HEADER


class VerifiableExecutionSystem:
    # the ves in uip
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

    def sessionSetupPrepare(self, op_intents_json):
        session_id = 0
        while session_id in self.txs_pool:
            session_id = randint(0, 0xffffffff)

        # test by stable sid
        session_id = 1

        # pre-register
        self.txs_pool[session_id] = VerifiableExecutionSystem.INITIAL_SESSION

        # create txs
        tx_intents, op_owners = VerifiableExecutionSystem.buildGraph(op_intents_json)

        wait_user = set(op_owners)
        for owner in op_owners:
            if owner not in self.user_pool:
                raise Missing(owner + " is not in user-pool")

        # initalize ack_dict
        self.txs_pool[session_id]['ack_dict'] = dict((owner, None) for owner in wait_user)
        self.txs_pool[session_id]['ack_counter'] = len(wait_user)

        sign_content = [str(session_id), tx_intents.purejson()]
        sign_bytes = HexBytes(rlp.encode(sign_content)).hex()
        atte_v = self.sign(sign_bytes)
        self.txs_pool[session_id]['ack_dict']['self_first'] = atte_v

        # TODO: build ISC
        isc = InsuranceSmartContract(
            sign_bytes,
            atte_v,
            [self.address] + ChainDNS.gatherusers(op_owners, userformat='dot-concated'),
            ves=self,
            # test by deployed contract
            tx_head={'from': self.address, 'gas': hex(400000)},
            contract_addr="0xd42e20871a72261ab4fce0057d9d31781ee5b731"
        )
        print(isc.__dict__)
        # TODO: async - send tx_intents
        return sign_content, atte_v

    def sessionSetupUpdate(self, session_id, ack_user_name, ack_signature):
        if session_id not in self.txs_pool:
            return KeyError("session (id=" + str(session_id) + ") is not valid anymore")

        if ack_user_name not in self.txs_pool[session_id]['ack_dict']:
            return Missing('You have no right to vote on this session')

        if ack_signature is None:
            self.txs_pool.pop(session_id)
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

        if self.txs_pool[session_id]['ack_counter'] == 0:
            self.sessionSetupFinish(session_id)

    def sessionSetupFinish(self, session_id):
        # TODO: Send Request(Tx-intents) NSB

        # TODO: inform Stake Funds
        pass

    @staticmethod
    def buildGraph(op_intents_json):
        # build eligible Op intents
        op_intents, op_owners = OpIntent.createopintents(op_intents_json['Op-intents'])

        # Generate Transaction intents and Dependency Graph
        # TODO:sort Graph
        return TransactionIntents(op_intents, op_intents_json['dependencies']), op_owners

    def sendTxInfoToNSB(self, info):
        pass

    def sendTxInfoTodApp(self, info):
        pass

    def stakefunded(self, isc, session_id):
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

    def addAttestation(self, session_id, atte):
        pass

    def addMerkleProof(self, session_id, merk):
        pass

    # tmp function
    def appenduserlink(self, users):
        if isinstance(users, list):
            for user in users:
                self.appenduserlink(user)
        else:  # assuming be class dApp
            self.user_pool[users.name] = users
