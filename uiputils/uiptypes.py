
'some types'

import json

from .eth.ethtypes import NetStatusBlockchain as ethNSB
from random import randint
from .uiperror import InitializeError, GenerationError, Missing
from uiputils.eth import JsonRPC

from uiputils.eth.ethtypes import Transaction as EthTx
from uiputils.config import eth_blockchain_info


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
    Key_Attribute_All = ('name', 'op_type')
    Key_Attribute_Payment = ('amount', 'src', 'dst')
    Key_Attribute_ContractInvocation = ('invoker', 'contract_domain', 'func', 'parameters')
    Op_Type = ('Payment', 'ContractInvocation')
    Chain_Default_Unit = {
        'Ethereum': 'wei'
    }

    def __init__(self, intent_json):
        self.op_type = ""
        for key_attr in OpIntent.Key_Attribute_All:
            if key_attr in intent_json:
                setattr(self, key_attr, intent_json[key_attr])
            else:
                raise InitializeError("the attribute " + key_attr + " must be included in the Op intent")

        if self.op_type not in OpIntent.Op_Type:
            raise InitializeError("unexpected op_type: " + self.op_type)

        getattr(self, self.op_type + 'Init')(intent_json)

    def PaymentInit(self, intent_json):
        for key_attr in OpIntent.Key_Attribute_Payment:
            if key_attr in intent_json:
                setattr(self, key_attr, intent_json[key_attr])
            else:
                raise InitializeError("the attribute " + key_attr + " must be included in the Payment intent")
        if 'unit' in intent_json:
            setattr(self, 'unit', intent_json['unit'])
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


def createopintents(op_intents_json):
    return [OpIntent(op_intent_json) for op_intent_json in op_intents_json]


class TransactionIntent:
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
                eth_blockchain_info[src_chain_id]['user'][op_intent.src['user_name']],
                eth_blockchain_info[src_chain_id]['relay'],  # dst_addr
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
                eth_blockchain_info[dst_chain_id]['user'][op_intent.dst['user_name']],  # src_addr
                eth_blockchain_info[dst_chain_id]['relay'],  # dst_addr
                op_intent.amount,  # fund
                op_intent.unit  # fund_unit
            )
            self.intents.append(tx)
            tx.tx_info['name'] = "T" + str(len(self.intents))
        else:
            raise GenerationError("unsupported chain-type: " + src_chain_type)

        intent_tx[op_intent.name] = ["T" + str(len(self.intents) - 1), "T" + str(len(self.intents))]

    def ContractInvocationTxGenerate(self, op_intent, intent_tx):
        chain_type, chain_id = op_intent.contract_domain.split('://')

        # assert (hasattr(op_intent, 'address') ^ hasattr(op_intent, 'code')) == 1

        if chain_type == "Ethereum":
            compare_vector = hasattr(op_intent, 'address') << 1 | hasattr(op_intent, 'func')
            if compare_vector == 3:  # deployed address + invoke function
                tx = EthTx(
                    "invoke",
                    chain_id,
                    op_intent.invoker,
                    op_intent.address,
                    op_intent.func,
                    op_intent.parameters
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
                    op_intent.invoker,
                    "@T" + str(len(self.intents)) + ".address",
                    op_intent.func,
                    op_intent.parameters
                )
                self.intents.append(tx)
                tx.tx_info['name'] = "T" + str(len(self.intents))
                intent_tx[op_intent.name] = ["T" + str(len(self.intents) - 1), "T" + str(len(self.intents))]
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

    def jsonize(self):
        return json.dumps(self.dictize(), sort_keys=True, indent=4, separators=(', ', ': '))

class DApp:
    def __init__(self, addr):
        self.address = addr

    def send(self, trans):
        chain_type, chain_id = trans['chain'].split('@')
        if chain_type == 'Ethereum':
            trans.
            packet_transaction = JsonRPC.ethSendTransaction(transaction)
            tx_response = JsonRPC.send(packet_transaction, HTTP_HEADER, host)
            tx_hash = tx_response['result']
            query = JsonRPC.ethGetTransactionReceipt(tx_hash)
        else:
            raise TypeError("unsupported chain-type: ", + chain_type)