
from uiputils.errors import InitializeError


def encode_parameters(origin_dict: dict):
    para_list, type_list = [], []
    for para_pair in origin_dict:
        if 'constant' in para_pair['Value']:
            para_list.append(para_pair['Value']['constant'])
        else:
            para_list.append('@' + para_pair['Value']['contract'] + '.' + para_pair['Value']['pos'])
        type_name = para_pair['Type']
        if type_name == 'uint':
            type_name = 'uint256'
        type_list.append(type_name)
    return para_list, type_list


class OpIntents:
    Key_Attribute_All = ('name', 'op_type')
    Key_Attribute_Payment = ('amount', 'src', 'dst')
    Key_Attribute_ContractInvocation = ('invoker', 'contract_domain', 'func', 'parameters')
    Option_Attribute_Payment = ('unit',)
    Option_Attribute_ContractInvocation = ()
    Op_Type = ('Payment', 'ContractInvocation')
    Chain_Default_Unit = {
        'Ethereum': 'wei',
        'EOS': 'SYS',
        'Tendermint': 'iew',
    }

    def __init__(self, intent_json):
        self.op_type = ""
        self.owners = []
        for key_attr in OpIntents.Key_Attribute_All:
            if key_attr in intent_json:
                setattr(self, key_attr, intent_json[key_attr])
            else:
                raise InitializeError("the attribute " + key_attr + " must be included in the Op intent")

        if self.op_type not in OpIntents.Op_Type:
            raise InitializeError("unexpected op_type: " + self.op_type)

        getattr(self, self.op_type + 'Init')(intent_json)

    @staticmethod
    def createopintents(op_intents_json):
        op_intents, op_owners = [], set()
        for op_intent_json in op_intents_json:
            op_intent = OpIntents(op_intent_json)
            op_intents.append(op_intent)
            op_owners.update(op_intent.owners)
        return op_intents, op_owners

    def PaymentInit(self, intent_json):
        for key_attr in OpIntents.Key_Attribute_Payment:
            if key_attr in intent_json:
                setattr(self, key_attr, intent_json[key_attr])
            else:
                raise InitializeError("the attribute " + key_attr + " must be included in the Payment intent")
        self.owners.extend([
            getattr(self, 'src')['domain'] + '.' + getattr(self, 'src')['user_name'],
            getattr(self, 'dst')['domain'] + '.' + getattr(self, 'dst')['user_name']
        ])
        for option_attr in OpIntents.Option_Attribute_Payment:
            if option_attr in intent_json:
                setattr(self, option_attr, intent_json[option_attr])
        else:
            chain_type = getattr(self, 'src')['domain'].split('://')[0]
            setattr(self, 'unit', OpIntents.Chain_Default_Unit[chain_type])

    def ContractInvocationInit(self, intent_json):
        for key_attr in OpIntents.Key_Attribute_ContractInvocation:
            if key_attr in intent_json:
                setattr(self, key_attr, intent_json[key_attr])
            else:
                raise InitializeError(
                    "the attribute " + key_attr +
                    " must be included in the ContractInvocation intent"
                )
        self.owners.append(getattr(self, 'contract_domain') + '.' + getattr(self, 'invoker'))
        for option_attr in OpIntents.Option_Attribute_ContractInvocation:
            if option_attr in intent_json:
                setattr(self, option_attr, intent_json[option_attr])

        # parameter encodes
        parameters, parameters_description = \
            encode_parameters(intent_json['parameters'])

        setattr(self, 'parameters', parameters)
        setattr(self, 'parameters_description', parameters_description)

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
