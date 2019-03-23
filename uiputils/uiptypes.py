
'some types'

# python modules
import json

# ethereum modules
from eth_hash.auto import keccak
from hexbytes import HexBytes

# uip modules
from .uiperror import InitializeError, GenerationError

# eth modules
from .eth.ethtypes import NetStatusBlockchain as ethNSB
from uiputils.eth.ethtypes import(
    Transaction as EthTx,
    ChainDNS as EthChainDNS
)

# constant
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
