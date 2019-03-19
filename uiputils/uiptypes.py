
'some types'

# python modules
import json
import time
import rlp
from random import randint

# ethereum modules
from eth_keys import keys, KeyAPI
from eth_hash.auto import keccak
from hexbytes import HexBytes

# uip modules
from .uiperror import InitializeError, GenerationError, Missing

# eth modules
from .eth.ethtypes import NetStatusBlockchain as ethNSB
from uiputils.eth import JsonRPC
from uiputils.eth.ethtypes import(
    Transaction as EthTx,
    ChainDNS as EthChainDNS
)

# config
from uiputils.config import eth_blockchain_info, HTTP_HEADER
ENC = 'utf-8'


def adduser_f00(user):
    user_name, chain_domain = (split_str[::-1] for split_str in user[::-1].split('.', 1))
    chain_type, chain_id = chain_domain.split('://')
    return ChainDNS.checkuser(chain_type, chain_id, user_name)

class ChainDNS:
    DNSmethod = {
       'Ethereum': EthChainDNS
    }
    adduser = {
        'dot-concated': adduser_f00
    }

    @staticmethod
    def checkuser(chain_type, chain_id, user_name):
        # this function doesn't check chain_type
        return ChainDNS.DNSmethod[chain_type].checkuser(chain_id, user_name)

    @staticmethod
    def checkrelay(chain_type, chain_id):
        # this function doesn't check chain_type
        return ChainDNS.DNSmethod[chain_type].checkrelay(chain_id)

    @staticmethod
    def gethost(chain_type, chain_id):
        return ChainDNS.DNSmethod[chain_type].gethost(chain_id)

    @staticmethod
    def gatherusers(users, userformat=None):
        if userformat is None:
            # TODO: multi-format of ChainDNS.gatherusers
            pass
        users_address = []
        if userformat == 'dot-concated':
            for formated_user in users:
                users_address.append(ChainDNS.adduser['dot-concated'](formated_user))
        else:
            raise KeyError(userformat + ' unsupported now')
        return users_address


class BlockchainNetwork:
    def __init__(self, identifer="", rpc_port=0, data_dir="", listen_port=0, host="", public=False):
        self.identifer = identifer
        self.rpc_port = rpc_port
        self.data_dir = data_dir
        self.listen_port = listen_port
        self.host = host
        self.public = public


class SmartContract:
    # The abstracted structure of a SmartContract.
    def __init__(self, bytecode="", domain="", name="", gas=hex(0), value=hex(0)):
        self.bytecode = bytecode
        self.domain = domain
        self.name = name
        self.gas = gas
        self.value = value


class StateProof:
    # The Merkle Proof for a Blockchain state.
    def __init__(self, value, block, proof):
        self.value = value
        self.block = block
        self.proof = proof

    def __str__(self):
        return "value: %s;block: %s;proof: %s;" % (self.value, self.block, self.proof)


class NetworkStatusBlockChain:
    def __init__(self, nsb_type="ethereum", *args, **kwargs):
        if nsb_type == "ethereum":
            self.handle = ethNSB(*args, **kwargs)
        else:
            self.handle = None
            raise TypeError("other NSB type not implemented")


class VerifiableExecutionSystem:
    # the ves in uip
    INVALID = 0
    INITIAL_SESSION = {
        'tx_intents': None,
        'Atte': {},
        'Merk': {},
        'ack_dict': {},
        'ack_counter': 0
    }

    def __init__(self):
        # temporary private-key
        self.key = keys.PrivateKey(b'\x01' * 32)
        ########################################

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

        # pre-register
        self.txs_pool[session_id] = VerifiableExecutionSystem.INITIAL_SESSION

        # build eligible Op intents
        op_intents, op_owners = OpIntent.createopintents(op_intents_json['Op-intents'])
        # initalize ack_dict
        self.txs_pool[session_id]['ack_dict'] = dict((owner, None) for owner in op_owners)

        # Generate Transaction intents and Dependency Graph
        tx_intents = TransactionIntents(op_intents, op_intents_json['dependencies'])

        # TODO: Sort Graph

        # TODO: build ISC
        isc = InsuranceSmartContract(tx_intents, ChainDNS.gatherusers(op_owners, userformat='dot-concated'))
        wait_user = set()
        for owner in op_owners:
            # test updateFunds
            isc.updateFunds(adduser_f00(owner), 0)
            ######################################

            if owner not in self.user_pool:
                raise Missing(owner + " is not in user-pool")
            wait_user.add(self.user_pool[owner])

        sign_content = [str(session_id), tx_intents.purejson(), isc.address]
        atte_v = self.sign(rlp.encode(sign_content))
        self.txs_pool[session_id]['ack_dict']['self_first'] = atte_v.to_hex()

        # TODO: async - send tx_intents
        return sign_content, atte_v

    def sessionSetupUpdate(self, session_id, ack_user_name, ack_signature):
        # TODO: Wait Approve Atte_V_D
        if session_id not in self.txs_pool:
            return KeyError("session (id=" + str(session_id) + ") is not valid anymore")
        if ack_signature is None:
            self.txs_pool.pop(session_id)

        # TODO: Verify ack_signature

        self.txs_pool[session_id]['ack_dict'][ack_user_name] = ack_signature

    def sessionSetupFinish(self, session_id):
        # TODO: Send Request(Tx-intents) NSB

        # TODO: Stake Funds
        pass

    def buildGraph(self, tx_intents):
        pass

    def sendTxInfoToNSB(self, info):
        pass

    def sendTxInfoTodApp(self, info):
        pass

    def stakefunded(self, isc, session_id):
        pass

    def sign(self, msg):
        return self.key.sign_msg(msg)

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


class InsuranceSmartContract:
    def __init__(self, info, owners):

        # TODO : contract construct
        self.address = '0xca35b7d915458ef540ade6068dfe2f44e8fa733c'
        self.contract = info
        self.owners = owners
        # self.handle = ethISC(...)
        # Insurance Smart Contract is a contract on the blockchain
        pass

    def updateFunds(self, owner, fund):
        if owner not in self.owners:
            raise Missing('this address is not owner')
        print(owner, "updated fund:", fund)

    def insuranceClaim(self, contract_id, atte):
        pass

    def settleContract(self, contract_id):
        pass


class OpIntent:
    Key_Attribute_All = ('name', 'op_type')
    Key_Attribute_Payment = ('amount', 'src', 'dst')
    Key_Attribute_ContractInvocation = ('invoker', 'contract_domain', 'func')
    Option_Attribute_Payment = ('unit',)
    Option_Attribute_ContractInvocation = ('parameters', 'parameters_description')
    Op_Type = ('Payment', 'ContractInvocation')
    Chain_Default_Unit = {
        'Ethereum': 'wei'
    }

    def __init__(self, intent_json):
        self.op_type = ""
        self.owners = []
        for key_attr in OpIntent.Key_Attribute_All:
            if key_attr in intent_json:
                setattr(self, key_attr, intent_json[key_attr])
            else:
                raise InitializeError("the attribute " + key_attr + " must be included in the Op intent")

        if self.op_type not in OpIntent.Op_Type:
            raise InitializeError("unexpected op_type: " + self.op_type)

        getattr(self, self.op_type + 'Init')(intent_json)

    @staticmethod
    def createopintents(op_intents_json):
        op_intents, op_owners = [], set()
        for op_intent_json in op_intents_json:
            op_intent = OpIntent(op_intent_json)
            op_intents.append(op_intent)
            op_owners.update(op_intent.owners)
        return op_intents, op_owners

    def PaymentInit(self, intent_json):
        for key_attr in OpIntent.Key_Attribute_Payment:
            if key_attr in intent_json:
                setattr(self, key_attr, intent_json[key_attr])
            else:
                raise InitializeError("the attribute " + key_attr + " must be included in the Payment intent")
        self.owners.extend([
            getattr(self, 'src')['domain'] + '.' + getattr(self, 'src')['user_name'],
            getattr(self, 'dst')['domain'] + '.' + getattr(self, 'dst')['user_name']
        ])
        for option_attr in OpIntent.Option_Attribute_Payment:
            if option_attr in intent_json:
                setattr(self, option_attr, intent_json[option_attr])
        else:
            chain_type = getattr(self, 'src')['domain'].split('://')[0]
            setattr(self, 'unit', OpIntent.Chain_Default_Unit[chain_type])

    def ContractInvocationInit(self, intent_json):
        for key_attr in OpIntent.Key_Attribute_ContractInvocation:
            if key_attr in intent_json:
                setattr(self, key_attr, intent_json[key_attr])
            else:
                raise InitializeError("the attribute " + key_attr +\
                                      " must be included in the ContractInvocation intent")
        self.owners.append(getattr(self, 'contract_domain') + '.' + getattr(self, 'invoker'))
        for option_attr in OpIntent.Option_Attribute_ContractInvocation:
            if option_attr in intent_json:
                setattr(self, option_attr, intent_json[option_attr])

        compare_vector = ('contract_addr' not in intent_json or intent_json['contract_addr'] is None) << 1 |\
                         ('contract_code' not in intent_json or intent_json['contract_code'] is None)

        if compare_vector == 3:
            raise InitializeError("only one of contract_addr and contract_code can be in the ContractInvocation intent")
        elif compare_vector == 0:
            raise InitializeError("either contract_addr or contract_code must be in the ContractInvocation intent")
        elif compare_vector == 2:  # code in intent
            setattr(self, 'code', intent_json['contract_code'])
        else:  # address in intent
            setattr(self, 'address', intent_json['contract_addr'])


class TransactionIntents:
    def __init__(self, op_intents, dependencies):
        self.intents = []
        self.dependencies = []
        intent_tx = {}
        for op_intent in op_intents:
            getattr(self, op_intent.op_type + "TxGenerate")(op_intent, intent_tx)

        # print generated OpX -> TxXs
        # for k, vs in intent_tx.items():
        #     print(k)
        #     for v in vs:
        #         print("   ", v)

        # build Dependencies
        for dependency in dependencies:
            if 'left' not in dependency or 'right' not in dependency:
                raise GenerationError("attribute left/right missing")

            if 'dep' not in dependency or dependency['dep'] == 'before':  # OpX before OpY (default relation)
                for u in intent_tx[dependency['left']]:
                    for v in intent_tx[dependency['right']]:
                        self.dependencies.append(u + "->" + v)
            elif dependency['dep'] == 'after':  # OpX after OpY
                for u in intent_tx[dependency['right']]:
                    for v in intent_tx[dependency['left']]:
                        self.dependencies.append(u + "->" + v)
            else:
                raise GenerationError('unsupported dependency-type: ' + dependency['dep'])

    def PaymentTxGenerate(self, op_intent, intent_tx):
        src_chain_type, src_chain_id = op_intent.src['domain'].split('://')
        dst_chain_type, dst_chain_id = op_intent.dst['domain'].split('://')

        if src_chain_type == "Ethereum":
            tx = EthTx(
                "transfer",  # transaction type
                src_chain_id,  # chain_id
                ChainDNS.checkuser(src_chain_type, src_chain_id, op_intent.src['user_name']),  #src_addr
                ChainDNS.checkrelay(src_chain_type, src_chain_id),  # dst_addr
                op_intent.amount,  # fund
                op_intent.unit  # fund_unit
            )
            self.intents.append(tx)
            tx.tx_info['name'] = "T" + str(len(self.intents))
        else:
            raise GenerationError("unsupported chain-type: " + src_chain_type)

        if dst_chain_type == "Ethereum":
            tx = EthTx(
                "transfer",  # transaction type
                dst_chain_id,  # chain_id
                ChainDNS.checkuser(dst_chain_type, dst_chain_id, op_intent.dst['user_name']),  # src_addr
                ChainDNS.checkrelay(dst_chain_type, dst_chain_id),  # dst_addr
                op_intent.amount,  # fund
                getattr(op_intent, 'unit')  # option fund_unit
            )
            self.intents.append(tx)
            tx.tx_info['name'] = "T" + str(len(self.intents))
        else:
            raise GenerationError("unsupported chain-type: " + dst_chain_type)

        t_fr, t_to = "T" + str(len(self.intents) - 1), "T" + str(len(self.intents))
        intent_tx[op_intent.name] = [t_fr, t_to]
        self.dependencies.append(t_fr + "->" + t_to)

    def ContractInvocationTxGenerate(self, op_intent, intent_tx):
        chain_type, chain_id = op_intent.contract_domain.split('://')

        # assert (hasattr(op_intent, 'address') ^ hasattr(op_intent, 'code')) == 1

        if chain_type == "Ethereum":
            invoker_address = ChainDNS.checkuser(chain_type, chain_id, op_intent.invoker)
            compare_vector = hasattr(op_intent, 'address') << 1 | hasattr(op_intent, 'func')
            if compare_vector == 3:  # deployed address + invoke function
                tx = EthTx(
                    "invoke",
                    chain_id,
                    invoker_address,
                    op_intent.address,
                    op_intent.func,
                    getattr(op_intent, 'parameters'),
                    getattr(op_intent, 'parameters_description')
                )
                self.intents.append(tx)
                tx.tx_info['name'] = "T" + str(len(self.intents))
                intent_tx[op_intent.name] = ["T" + str(len(self.intents))]
            elif compare_vector == 2:  # deployed address
                print("warning: transaction", len(self.intents) + 1, "has no effect")
                tx = EthTx('void')
                self.intents.append(tx)
                tx.tx_info['name'] = "T" + str(len(self.intents))
                intent_tx[op_intent.name] = ["T" + str(len(self.intents))]
            elif compare_vector == 1:  # deploy address + invoke function
                tx = EthTx(
                    "deploy",
                    chain_id,
                    op_intent.code,
                    gasuse=hex(200000)  # op_intent.gas
                )
                self.intents.append(tx)
                tx.tx_info['name'] = "T" + str(len(self.intents))
                tx = EthTx(
                    "invoke",
                    chain_id,
                    invoker_address,
                    "@T" + str(len(self.intents)) + ".address",
                    op_intent.func,
                    op_intent.parameters,
                    op_intent.parameters_description
                )
                self.intents.append(tx)
                tx.tx_info['name'] = "T" + str(len(self.intents))
                t_fr, t_to = "T" + str(len(self.intents) - 1), "T" + str(len(self.intents))
                intent_tx[op_intent.name] = [t_fr, t_to]
                self.dependencies.append(t_fr + "->" + t_to)
            else:  # depoly address
                tx = EthTx(
                    "deploy",
                    chain_id,
                    op_intent.code,
                    gasuse=op_intent.gas
                )
                self.intents.append(tx)
                tx.tx_info['name'] = "T" + str(len(self.intents))
                intent_tx[op_intent.name] = ["T" + str(len(self.intents))]
        else:
            raise GenerationError("unsupported chain-type: " + chain_type)

    def dictize(self):
        return {
            'intents': [tx.tx_info for tx in self.intents],
            'dependencies': self.dependencies
        }

    def purejson(self):
        return json.dumps(self.dictize(), sort_keys=True)

    def jsonize(self):
        return json.dumps(self.dictize(), sort_keys=True, indent=4, separators=(', ', ': '))

    def hash(self):
        return HexBytes(keccak(bytes(json.dumps(self.dictize(), sort_keys=True).encode(ENC)))).hex()

class DApp:
    def __init__(self, user_loc):
        self.info = {}
        chain_type, chain_id = user_loc['domain'].split('://')
        self.address = ChainDNS.checkuser(chain_type, chain_id, user_loc['name'])
        self.chain_host = ChainDNS.gethost(chain_type, chain_id)
        self.name = user_loc['domain'] + '.' + user_loc['name']
        if 'passphrase' in user_loc:
            self.password = user_loc['passphrase']
        # for loc in user_loc:
        #     chain_type, chain_id = loc['chain'].split('://')
        #     if chain_type == 'Ethereum':
        #         self.address = ChainDNS.checkuser(chain_type, chain_id, loc['name'])
        #         self.chain_host = ChainDNS.gethost(chain_type, chain_id)
        #         if 'passphrase' in loc:
        #             self.password = loc['passphrase']
        #     self.info[chain_type] = {
        #         'address': ChainDNS.checkuser(chain_type, chain_id, loc['name']),
        #         'host': ChainDNS.gethost(chain_type, chain_id),
        #         'password': None
        #     }
        #     if 'passphrase' in loc:
        #         self.info[chain_type]['password'] = loc['passphrase']

    def unlockself(self):
        unlock = JsonRPC.personalUnlockAccount(self.address, self.password, 20)
        response = JsonRPC.send(unlock, HTTP_HEADER, self.chain_host)
        if not response['result']:
            raise ValueError("unlock failed. wrong password?")

    def sign(self, msg):
        # assuming self.address is on Ethereum
        self.unlockself()
        sign_json = JsonRPC.ethSign(self.address, msg)
        response = JsonRPC.send(sign_json, HTTP_HEADER, self.chain_host)['result']
        print(response)

    def call(self, trans):
        if trans.chain_type == 'Ethereum':
            call_json = JsonRPC.ethCall(trans.jsonize())
            tx_response = JsonRPC.send(call_json, HTTP_HEADER, trans.chain_host)['result']
            # print(json.dumps(tx_response, sort_keys=True, indent=4, separators=(', ', ': ')))

            print(tx_response)

        else:
            raise TypeError("unsupported chain-type: ", + trans.chain_type)

    def send(self, trans, passphrase):
        if trans.chain_type == 'Ethereum':
            unlock = JsonRPC.personalUnlockAccount(self.address, passphrase, 20)
            tx_response = JsonRPC.send(unlock, HTTP_HEADER, trans.chain_host)
            print(json.dumps(tx_response, sort_keys=True, indent=4, separators=(', ', ': ')))
            packet_transaction = JsonRPC.ethSendTransaction(trans.jsonize())
            tx_response = JsonRPC.send(packet_transaction, HTTP_HEADER, trans.chain_host)
            print(json.dumps(tx_response, sort_keys=True, indent=4, separators=(', ', ': ')))
            tx_hash = tx_response['result']
            query = JsonRPC.ethGetTransactionReceipt(tx_hash)
            while True:
                tx_response = JsonRPC.send(query, HTTP_HEADER, trans.chain_host)
                if tx_response['result'] is None:
                    print("transacting")
                    time.sleep(2)
                    continue
                break
            print(json.dumps(tx_response, sort_keys=True, indent=4, separators=(', ', ': ')))
        else:
            raise TypeError("unsupported chain-type: ", + trans.chain_type)

    def ackinit(self, ves: VerifiableExecutionSystem, content: list, sig: KeyAPI.Signature):
        # TODO: verify signature

        # TODO: sign
        signatrue = "123456"
        ves.sessionSetupUpdate(int(content[0]), self.name, signatrue)
