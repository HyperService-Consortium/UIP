
# python modules
import json

# ethereum modules
from eth_hash.auto import keccak
from hexbytes import HexBytes

# uip modules
from uiputils.errors import GenerationError
from uiputils.chain_dns import ChainDNS

# eth modules
from uiputils.ethtools import hex_match, hex_match_withprefix

# config
from uiputils.config import (
    eth_unit_factor,
    tennsb_unit_factor
)

# constant
MOD6 = (1 << 6) - 1


class Transaction(object):
    def __init__(self):
        self._host = ""
        self._trans_info = {}

    def __str__(self):
        return 'chain_host: ' + str(self._host) +\
               '\ntransaction_intent: ' + str(self._trans_info)

    @property
    def host(self):
        return self._host

    @property
    def src(self):
        return self._trans_info['src']

    @src.setter
    def src(self, value):
        self._trans_info['src'] = value

    @property
    def dst(self):
        return self._trans_info['dst']

    @dst.setter
    def dst(self, value):
        self._trans_info['dst'] = value

    @property
    def meta(self):
        return self._trans_info

    @meta.setter
    def meta(self, value):
        # TODO: json
        if not isinstance(value, dict):
            raise TypeError("meta must be dict (TODO: or json)")
        if 'src' not in value:
            raise KeyError("meta must have key 'src'")
        if 'dst' not in value:
            raise KeyError("meta must have key 'dst'")
        self._trans_info = value

    def purejson(self):
        return json.dumps(self.__dict__, sort_keys=True)

    def pretjson(self):
        return json.dumps(self.__dict__, sort_keys=True, indent=4, separators=(', ', ': '))

    def make_intent(self):
        return {
            'src': HexBytes(self.src),
            'dst': HexBytes(self.dst),
            'amt': 0,
            'meta': self.purejson().encode()
        }


class PaymentTransaction(Transaction):
    def __init__(self):
        super().__init__()


class InvokeTransaction(Transaction):
    def __init__(self):
        super().__init__()
        self._parameters_description = []

    @property
    def parameters_description(self):
        return self._parameters_description

    @parameters_description.setter
    def parameters_description(self, value):
        if not isinstance(value, list) and value is not None:
            raise TypeError("parameters description must be list")
        self._parameters_description = value


class EthPaymentTransaction(PaymentTransaction):
    def __init__(self, op_intent):
        super().__init__()
        self._host = op_intent.host
        self._trans_info = {
            'src': op_intent.src,
            'dst': op_intent.dst,
            'value': op_intent.amount * eth_unit_factor[op_intent.unit],
        }


class TenPaymentTransaction(PaymentTransaction):
    def __init__(self, op_intent):
        super().__init__()
        self._host = op_intent.host
        self._trans_info = {
            'src': op_intent.src,
            'dst': op_intent.dst,
            'value': op_intent.amount * tennsb_unit_factor[op_intent.unit],
        }


class EthInvokeTransaction(InvokeTransaction):
    def __init__(self, op_intent):
        super().__init__()
        self._host = op_intent.host
        self.parameters_description = op_intent.parameters_description

        if len(op_intent.func) == 8 and hex_match.match(op_intent.func):
            self.signature = op_intent.func
        elif len(op_intent.func) == 10 and hex_match_withprefix.match(op_intent.func):
            self.signature = op_intent.func[2:]
        elif op_intent.parameters_description is not None:
            self.signature = HexBytes(keccak(bytes(
                (op_intent.func + '(' + ','.join(op_intent.parameters_description) + ')').encode('utf-8')
            ))[0:4]).hex()
        else:  # function_parameters_description is None
            raise GenerationError('function-signatrue can\'t be generated')

        self._trans_info = {
            'src': op_intent.invoker,
            'dst': op_intent.address,
            'func': op_intent.func,
            'parameters': op_intent.parameters,
        }


class TenInvokeTransaction(InvokeTransaction):
    def __init__(self, op_intent):
        super().__init__()
        self._host = op_intent.host
        self.parameters_description = op_intent.parameters_description
        self._trans_info = {
            'src': op_intent.invoker,
            'dst': op_intent.address,
            'func': op_intent.func,
            'parameters': op_intent.parameters,
        }


def _make_payment_trans(op_intent):
    # more efficient
    src = op_intent.src
    dst = op_intent.dst

    # more safe
    # src = op_intent.src.copy()
    # dst = op_intent.dst.copy()

    chain_type, chain_id = src['domain'].split('://')
    setattr(op_intent, 'host', ChainDNS.gethost(chain_type, chain_id))
    op_intent.src = ChainDNS.checkuser(chain_type, chain_id, src['user_name'])
    op_intent.dst = ChainDNS.checkrelay(chain_type, chain_id)
    yield TransactionHelper.payment_transaction_inject[chain_type](op_intent)

    chain_type, chain_id = dst['domain'].split('://')
    setattr(op_intent, 'host', ChainDNS.gethost(chain_type, chain_id))
    op_intent.src = ChainDNS.checkrelay(chain_type, chain_id)
    op_intent.dst = ChainDNS.checkuser(chain_type, chain_id, dst['user_name'])
    yield TransactionHelper.payment_transaction_inject[chain_type](op_intent)


def _make_invoke_trans(op_intent):
    chain_type, chain_id = op_intent.contract_domain.split('://')
    setattr(op_intent, 'host', ChainDNS.gethost(chain_type, chain_id))
    op_intent.invoker = ChainDNS.checkuser(chain_type, chain_id, op_intent.invoker)
    yield TransactionHelper.invoke_transaction_inject[chain_type](op_intent)


class TransactionHelper:
    payment_transaction_inject = {
        'Ethereum': EthPaymentTransaction,
        'Tendermint': TenPaymentTransaction
    }

    invoke_transaction_inject = {
        'Ethereum': EthInvokeTransaction,
        'Tendermint': TenInvokeTransaction
    }

    make_payment_trans = staticmethod(_make_payment_trans)
    make_invoke_trans = staticmethod(_make_invoke_trans)

    make_spec_trans = {
        'Payment': _make_payment_trans,
        'ContractInvocation': _make_invoke_trans
    }

    @staticmethod
    def make(spec, op_intent):
        return TransactionHelper.make_spec_trans[spec](op_intent)

    @staticmethod
    def maker(spec):
        return TransactionHelper.make_spec_trans[spec]

if __name__ == '__main__':
    from uiputils.op_intents.op_intents import OpIntent
    from uiputils.uiptools.cast import formated_json

    intent_json = {
        "name": "Op1",
        "op_type": "Payment",
        "src": {
            "domain": "Tendermint://chain2",
            "user_name": "a2"
        },
        "dst": {
            "domain": "Ethereum://chain3",
            "user_name": "a1"
        },
        "amount": 20,
        "unit": "iew"
    }

    intent = OpIntent(intent_json)

    print(formated_json(intent.__dict__))
    tr: list = [*TransactionHelper.make_payment_trans(intent)]

    print(*(t.__dict__ for t in tr))
    print(isinstance(tr[0], Transaction))
    print(isinstance(tr[1], Transaction))
    print(isinstance(tr[0], PaymentTransaction))
    print(isinstance(tr[1], PaymentTransaction))
    print(isinstance(tr[0], InvokeTransaction))
    print(isinstance(tr[1], InvokeTransaction))
    print(isinstance(tr[0], EthPaymentTransaction))
    print(isinstance(tr[0], TenPaymentTransaction))
    print(isinstance(tr[1], EthPaymentTransaction))
    print(isinstance(tr[1], TenPaymentTransaction))

    intent_json = {
        "op_type": "ContractInvocation",
        "name": "Op2",
        "invoker": "a1",
        "contract_domain": "Ethereum://chain3",
        "contract_addr": "0x27f8e035eb353bcefb348174205e90bc18ab3eda",
        "contract_code": None,
        "func": "deposit",
        "parameters": [
            {
                "Type": "uint256",
                "Value": {
                    "constant": "10"
                }
            }
        ]
    }

    intent = OpIntent(intent_json)

    print(formated_json(intent.__dict__))
    tr: list = [*TransactionHelper.make_invoke_trans(intent)]

    print(*(t.__dict__ for t in tr))
    print(isinstance(tr[0], Transaction))
    print(isinstance(tr[0], PaymentTransaction))
    print(isinstance(tr[0], InvokeTransaction))
    print(isinstance(tr[0], EthInvokeTransaction))
    print(isinstance(tr[0], TenInvokeTransaction))

    intent_json = {
        "op_type": "ContractInvocation",
        "name": "Op4",
        "invoker": "a3",
        "contract_domain": "Tendermint://chain1",
        "contract_addr": "0xe31ddd72dd2f601e1fd82372b898952cfcf6d78662bdf59297dd3ef8cca9ba46",
        "contract_code": None,
        "func": "BuyOption",
        "parameters": [
            {
                "Type": "uint256",
                "Value": {
                    "constant": "5"
                }
            }, {
                "Type": "uint256",
                "Value": {
                    "contract": "c1",
                    "field": "StrikePrice",
                    "pos": "0"
                }
            }
        ]
    }

    intent = OpIntent(intent_json)

    print(formated_json(intent.__dict__))
    tr: list = [*TransactionHelper.make_invoke_trans(intent)]

    print(*(t.__dict__ for t in tr))
    print(isinstance(tr[0], Transaction))
    print(isinstance(tr[0], PaymentTransaction))
    print(isinstance(tr[0], InvokeTransaction))
    print(isinstance(tr[0], EthInvokeTransaction))
    print(isinstance(tr[0], TenInvokeTransaction))

    tr: InvokeTransaction = tr[0]
    try:
        tr.parameters_description = ""
        print("good")
    except Exception as e:
        print(e)

    try:
        tr.parameters_description = []
        print("good")
    except Exception as e:
        print(e)

    try:
        tr.parameters_description = None
        print("good")
    except Exception as e:
        print(e)

    try:
        tr.meta = ""
        print("good")
    except Exception as e:
        print(e)

    try:
        tr.meta = None
        print("good")
    except Exception as e:
        print(e)

    try:
        tr.meta = {
            'src': "abcd",
            'to': "abcd"
        }
        print("good")
    except Exception as e:
        print(e)

    try:
        tr.meta = {
            'src': "abcd",
            'dst': "abcd"
        }
        print("good")
    except Exception as e:
        print(e)


