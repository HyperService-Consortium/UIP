
# python modules
import json

# ethereum modules
from eth_hash.auto import keccak
from hexbytes import HexBytes

# uip modules
from uiputils.errors import (
    GenerationError,
    Missing,
    Mismatch
)

# eth modules
from uiputils.ethtools import hex_match, hex_match_withprefix, AbiEncoder
from uiputils.dataparse.data_parser import EthDataParser

# config
from uiputils.config import (
    eth_default_gasuse,
    eth_blockchain_info,
    tennsb_blockchain_info,
    eth_unit_factor,
    tennsb_unit_factor
)

# constant
MOD6 = (1 << 6) - 1


class TenAny(object):
    pass


def temporary_generate_tendermint_transaction(transaction_type, *args, **kwargs):
    print(transaction_type, args, kwargs)

    if transaction_type == "transfer":
        transaction = TenAny()
        setattr(transaction, 'tx_info', {
            'trans_type': 'transfer',
            'chain': args[0],
            'source': args[1],
            'dst': args[2],
            'fund': 20,
            'unit': 'iew',
        })

        setattr(transaction, 'chain_host', tennsb_blockchain_info[args[0]]['host'])

        def tmp_jsonize():
            return {
                'trans_type': 'transfer',
                'chain': args[0],
                'source': args[1],
                'dst': args[2],
                'fund': 20,
                'unit': 'iew',
            }

        setattr(transaction, 'jsonize', tmp_jsonize)
        return transaction
    else:
        raise GenerationError("temporary testing...")


def transaction_creator(chain_type):
    if chain_type == "Ethereum":
        return EthTransaction
    elif chain_type == "Tendermint":
        return temporary_generate_tendermint_transaction
    else:
        raise GenerationError("unsupported chain-type: " + chain_type)


class EthTransaction:
    def __init__(self, transaction_type, *args, **kwargs):
        self.chain_host = ""
        self.chain_type = "Ethereum"
        self.tx_info = {}
        getattr(self, transaction_type + '_init')(*args, **kwargs)

    def transfer_init(self, chain_id, src_addr, dst_addr, fund, fund_unit, gasuse=eth_default_gasuse):
        self.chain_host = eth_blockchain_info[chain_id]['host']
        self.tx_info = {
            'trans_type': 'transfer',
            'chain': chain_id,
            'source': src_addr,
            'dst': dst_addr,
            'fund': hex(int(fund * eth_unit_factor[fund_unit])),
            'unit': 'wei',
            'gas': gasuse
        }

    def deploy_init(self, chain_id, code, gasuse=eth_default_gasuse):
        self.chain_host = eth_blockchain_info[chain_id]['host']
        self.tx_info = {
            'trans_type': 'deploy',
            'chain': chain_id,
            'code': code,
            'gas': gasuse
        }

    def invoke_init(
        self,
        chain_id,
        invoker,
        contract_address,
        function_name,
        function_parameters=None,
        function_parameters_description=None,
        gasuse=eth_default_gasuse
    ):
        # if function parameters' description is not given, the function_parameters must be in format string
        self.chain_host = eth_blockchain_info[chain_id]['host']
        self.tx_info = {
            'trans_type': 'invoke',
            'chain': chain_id,
            'invoker': invoker,
            'address': contract_address,
            'func': function_name,
            'parameters': function_parameters,
            'gas': gasuse
        }

        # generate signature
        if len(function_name) == 8 and hex_match.match(function_name):
            setattr(self, 'signature', function_name)
        elif len(function_name) == 10 and hex_match_withprefix.match(function_name):
            setattr(self, 'signature', function_name)
        elif function_parameters_description is not None:
            # print(self.tx_info['func'])
            # print(function_parameters_description)
            # import time
            # time.sleep(0.5)
            print(function_parameters_description)
            to_hash = bytes(
                (self.tx_info['func'] + '(' + ','.join(function_parameters_description) + ')').encode('utf-8')
            )
            signature = HexBytes(keccak(to_hash)[0:4]).hex()
            setattr(self, 'signature', signature)
        else:  # function_parameters_description is None
            raise GenerationError('function-signatrue can\'t be generated')

        setattr(self, 'parameters_description', function_parameters_description)

    def jsonize(self):
        return getattr(self, self.tx_info['trans_type'] + '_jsonize')()

    def transfer_jsonize(self):
        return {
            "from": self.tx_info['source'],
            "to": self.tx_info['dst'],
            "gas": self.tx_info['gas'],
            "value": self.tx_info['fund']
        }

    def deploy_jsonize(self):
        return {
            "from": "0x7019fa779024c0a0eac1d8475733eefe10a49f3b",
            "data": self.tx_info['code'],
            "gas": self.tx_info['gas'],
        }

    def invoke_jsonize(self):
        # self.tx_info['parameters']
        res = {
            "from": self.tx_info['invoker'],
            "to": self.tx_info['address'],
            "data": "",
            "gas": self.tx_info['gas']
        }
        if 'parameters' in self.tx_info:
            if hasattr(self, 'parameters_description'):
                parameters = EthDataParser.parse(self.tx_info['parameters'], getattr(self, 'parameters_description'))
                res['data'] = getattr(self, 'signature') + parameters
            else:  # without parameters_description
                if isinstance(self.tx_info['parameters'], str):
                    if not hex_match.match(self.tx_info['parameters']) and \
                            not hex_match_withprefix.match(self.tx_info['parameters']):
                        raise TypeError("bad encoded parameters given: not hexstring")
                    if self.tx_info['parameters'][1] == 'x':
                        if (len(self.tx_info['parameters']) - 2) & MOD6:
                            raise Mismatch("bad encoded parameters given: not multiple of 64(32 bytes)")
                        res['data'] = getattr(self, 'signature') + self.tx_info['parameters'][2:]
                    else:
                        if len(self.tx_info['parameters']) & MOD6:
                            raise Mismatch("bad encoded parameters given: not multiple of 64(32 bytes)")
                        res['data'] = getattr(self, 'signature') + self.tx_info['parameters']
                else:
                    raise Missing("no parameters_description to help encode the parameters")
        else:  # raw-function called
            res['data'] = self.tx_info['func']

        if 'value' in self.tx_info:
            res['value'] = self.tx_info['value']
        return res

    def __str__(self):
        return 'chain_host: ' + str(self.chain_host) +\
               '\ntransaction_intent: ' + str(self.tx_info)

    def purejson(self):
        return json.dumps(self.__dict__, sort_keys=True)

    def pretjson(self):
        return json.dumps(self.__dict__, sort_keys=True, indent=4, separators=(', ', ': '))


class TenTransaction:
    def __init__(self, transaction_type, *args, **kwargs):
        self.chain_host = ""
        self.chain_type = "Tendermint"
        self.tx_info = {}
        getattr(self, transaction_type + '_init')(*args, **kwargs)

    def transfer_init(self, chain_id, src_addr, dst_addr, fund, fund_unit):
        self.chain_host = tennsb_blockchain_info[chain_id]['host']
        self.tx_info = {
            'trans_type': 'transfer',
            'chain': chain_id,
            'source': src_addr,
            'dst': dst_addr,
            'fund': hex(int(fund * eth_unit_factor[fund_unit])),
            'unit': 'iew'
        }

    def deploy_init(self, chain_id, code):
        self.chain_host = tennsb_blockchain_info[chain_id]['host']
        self.tx_info = {
            'trans_type': 'deploy',
            'chain': chain_id,
            'code': code
        }

    def invoke_init(
        self,
        chain_id,
        invoker,
        contract_address,
        function_name,
        function_parameters=None,
        function_parameters_description=None
    ):
        # if function parameters' description is not given, the function_parameters must be in format string
        self.chain_host = tennsb_blockchain_info[chain_id]['host']
        self.tx_info = {
            'trans_type': 'invoke',
            'chain': chain_id,
            'invoker': invoker,
            'address': contract_address,
            'func': function_name,
            'parameters': function_parameters
        }
# TODO: Check TenNSB-----------------------------------------------------------------------------

        # generate signature
        if len(function_name) == 8 and hex_match.match(function_name):
            setattr(self, 'signature', function_name)
        elif len(function_name) == 10 and hex_match_withprefix.match(function_name):
            setattr(self, 'signature', function_name)
        elif function_parameters_description is not None:
            # print(self.tx_info['func'])
            # print(function_parameters_description)
            # import time
            # time.sleep(0.5)
            print(function_parameters_description)
            to_hash = bytes(
                (self.tx_info['func'] + '(' + ','.join(function_parameters_description) + ')').encode('utf-8')
            )
            signature = HexBytes(keccak(to_hash)[0:4]).hex()
            setattr(self, 'signature', signature)
        else:  # function_parameters_description is None
            raise GenerationError('function-signatrue can\'t be generated')

        setattr(self, 'parameters_description', function_parameters_description)

    def jsonize(self):
        return getattr(self, self.tx_info['trans_type'] + '_jsonize')()

    def transfer_jsonize(self):
        return {
            "from": self.tx_info['source'],
            "to": self.tx_info['dst'],
            "gas": self.tx_info['gas'],
            "value": self.tx_info['fund']
        }

    def deploy_jsonize(self):
        return {
            "from": "0x7019fa779024c0a0eac1d8475733eefe10a49f3b",
            "data": self.tx_info['code'],
            "gas": self.tx_info['gas'],
        }

    def invoke_jsonize(self):
        # self.tx_info['parameters']
        res = {
            "from": self.tx_info['invoker'],
            "to": self.tx_info['address'],
            "data": "",
            "gas": self.tx_info['gas']
        }
        if 'parameters' in self.tx_info:
            if hasattr(self, 'parameters_description'):
                parameters = EthDataParser.parse(self.tx_info['parameters'], getattr(self, 'parameters_description'))
                res['data'] = getattr(self, 'signature') + parameters
            else:  # without parameters_description
                if isinstance(self.tx_info['parameters'], str):
                    if not hex_match.match(self.tx_info['parameters']) and \
                            not hex_match_withprefix.match(self.tx_info['parameters']):
                        raise TypeError("bad encoded parameters given: not hexstring")
                    if self.tx_info['parameters'][1] == 'x':
                        if (len(self.tx_info['parameters']) - 2) & MOD6:
                            raise Mismatch("bad encoded parameters given: not multiple of 64(32 bytes)")
                        res['data'] = getattr(self, 'signature') + self.tx_info['parameters'][2:]
                    else:
                        if len(self.tx_info['parameters']) & MOD6:
                            raise Mismatch("bad encoded parameters given: not multiple of 64(32 bytes)")
                        res['data'] = getattr(self, 'signature') + self.tx_info['parameters']
                else:
                    raise Missing("no parameters_description to help encode the parameters")
        else:  # raw-function called
            res['data'] = self.tx_info['func']

        if 'value' in self.tx_info:
            res['value'] = self.tx_info['value']
        return res

    def __str__(self):
        return 'chain_host: ' + str(self.chain_host) +\
               '\ntransaction_intent: ' + str(self.tx_info)

    def purejson(self):
        return json.dumps(self.__dict__, sort_keys=True)

    def pretjson(self):
        return json.dumps(self.__dict__, sort_keys=True, indent=4, separators=(', ', ': '))


