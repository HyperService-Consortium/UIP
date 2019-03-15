
'some types'

from .eth.ethtypes import NetStatusBlockchain as ethNSB
from random import randint
from .uiperror import InitializeError

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
    INVALID_TXS = [{}]
    def __init__(self):
        self.txs_pool = {
            0: (
                VerifiableExecutionSystem.INVALID,
                VerifiableExecutionSystem.INVALID_TXS
            )
        }
        self.isc = InsuranceSmartContract
        pass

    # async receiveIntents(self, intents):
    #     pass

    # async receiveTransactions(self, txs):
    #     pass

    def sessionSetup(self, txs):
        session_id = 0
        while session_id in self.txs_pool:
            session_id = randint(0, 0xffffffff)
        tx_graph = self.buildGraph(txs)

        # send atte_1 and get atte_12

        nsb_info, isc_info, dapp_info = self.generateTxInfo(tx_graph)

        tosend_dapps = set()
        for tx in txs:
            if 'from' in tx:
                tosend_dapps.add(tx['from'])
            if 'to' in tx:
                tosend_dapps.add(tx['to'])

        tovote = len(tosend_dapps)

        for dapp in tosend_dapps:
            tovote -= 1
            if dapp != "":
                pass

        if tovote == 0:
            self.sendTxInfoToNSB(nsb_info)
            isc = self.isc(isc_info, tosend_dapps)
            if self.stakefunded(isc, session_id):
                self.txs_pool[session_id]= session_id, txs

    def buildGraph(self, txs):
        pass

    def generateTxInfo(self, tx_graph):
        pass

    def sendTxInfoToNSB(self, info):
        pass

    def sendTxInfoTodApp(self, info):
        pass

    def stakefunded(self, isc, session_id):
        pass


class InsuranceSmartContract:
    isc_data = {}

    def __init__(self, info, owners):
        # self.handle = ethISC(...)
        # Insurance Smart Contract is a contract on the blockchain
        pass

    def updateFunds(self):
        pass

    def insuranceClaim(self, contract_id, atte):
        pass

    def settleContract(self, contract_id):
        pass


class OpIntent:
    Key_Attribute_All = ('name', 'intent_type')
    Key_Attribute_Payment = ('amount', 'src', 'dst')
    Key_Attribute_ContractInvocation = ('invoker', 'contract_domain', 'func', 'parameters')
    Intent_Type = ('Payment', 'ContractInvocation')
    Chain_Baseunit = {
        'Ethereum': 'wei'
    }

    def __init__(self, intent_json):
        self.intent_type = ""
        for key_attr in OpIntent.Key_Attribute_All:
            if key_attr in intent_json:
                setattr(self, key_attr, intent_json[key_attr])
            else:
                raise InitializeError("the attribute " + key_attr + " must be included in the Op intent")

        if self.intent_type not in OpIntent.Intent_Type:
            raise InitializeError("unexpected intent_type: " + self.intent_type)

        getattr(self, self.intent_type + 'Init')(intent_json)

    def PaymentInit(self, intent_json):
        for key_attr in OpIntent.Key_Attribute_Payment:
            if key_attr in intent_json:
                setattr(self, key_attr, intent_json[key_attr])
            else:
                raise InitializeError("the attribute " + key_attr + " must be included in the Payment intent")
        if 'unit' in intent_json:
            setattr(self, 'unit', intent_json['unit'])
        else:
            setattr(self, 'unit', OpIntent.Chain_Baseunit[getattr(self, 'src')['domain_type']])

    def ContractInvocationInit(self, intent_json):
        for key_attr in OpIntent.Key_Attribute_ContractInvocation:
            if key_attr in intent_json:
                setattr(self, key_attr, intent_json[key_attr])
            else:
                raise InitializeError("the attribute " + key_attr +\
                                      " must be included in the ContractInvocation intent")
        # "contract_addr": "addr",
        #         "contract_code": "code",
        compare_vector = ('contract_addr' not in intent_json or intent_json['contract_addr'] is None) << 1 |\
                         ('contract_code' not in intent_json or intent_json['contract_code'] is None)
        print(compare_vector)
        if compare_vector == 3:
            raise InitializeError("only one of contract_addr and contract_code can be in the ContractInvocation intent")
        elif compare_vector == 0:
            raise InitializeError("either contract_addr or contract_code must be in the ContractInvocation intent")
        elif compare_vector == 2:  # code in intent
            setattr(self, 'code', intent_json['contract_code'])
        else:  # address in intent
            setattr(self, 'address', intent_json['contract_addr'])


def createopintents(op_intents_json):
    return [OpIntent(op_intent_json) for op_intent_json in op_intents_json]
