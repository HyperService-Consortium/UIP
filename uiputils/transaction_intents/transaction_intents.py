import copy
import json
import queue

from eth_hash.auto import keccak
from hexbytes import HexBytes

from uiputils.transaction import (
    TransactionHelper
)

from uiputils.errors import GenerationError

ENC = 'utf-8'


class TransactionIntents:
    def __init__(self, op_intents=None, dependencies=None):
        self._intents: list = None
        self._belongs = None
        self._dependencies = None
        self._origin_intents = copy.copy(op_intents)
        self._dependencies = copy.copy(dependencies)

        # print generated OpX -> TxXs
        # for k, vs in intent_tx.items():
        #     print(k)
        #     for v in vs:
        #         print("   ", v)

        # build Dependencies
        # for dependency in dependencies:
        #     if 'left' not in dependency or 'right' not in dependency:
        #         raise GenerationError("attribute left/right missing")
        #
        #     if 'dep' not in dependency or dependency['dep'] == 'before':  # OpX before OpY (default relation)
        #         for u in intent_tx[dependency['left']]:
        #             for v in intent_tx[dependency['right']]:
        #                 self.dependencies.append(u + "->" + v)
        #     elif dependency['dep'] == 'after':  # OpX after OpY
        #         for u in intent_tx[dependency['right']]:
        #             for v in intent_tx[dependency['left']]:
        #                 self.dependencies.append(u + "->" + v)
        #     else:
        #         raise GenerationError('unsupported dependency-type: ' + dependency['dep'])

    @property
    def intents(self):
        if self._intents is None:
            self.sort(self._dependencies)
        return self._intents

    @property
    def belongs(self):
        if self._belongs is None:
            self.generate_from_opintents(self._origin_intents)
        return self._belongs

    @property
    def origin_intents(self):
        return self._origin_intents

    @origin_intents.setter
    def origin_intents(self, value):
        self._origin_intents = value
        self._belongs = None
        self._intents = None

    @property
    def dependencies(self):
        return self._dependencies

    @dependencies.setter
    def dependencies(self, value):
        self._dependencies = value
        self._intents = None

    def generate_from_opintents(self, op_intents=None):
        if op_intents is not None and self._origin_intents is not op_intents:
            self._origin_intents = copy.copy(op_intents)

        self._belongs = {}
        for op_intent in self._origin_intents:
            self._belongs[op_intent.name] = [*TransactionHelper.make(op_intent.op_type, op_intent)]
        return self._belongs

    def sort(self, dependencies=None):
        if dependencies is not None and self._dependencies is not dependencies:
            self._dependencies = copy.copy(dependencies)
        if self._belongs is None:
            self.generate_from_opintents(self._origin_intents)

        self._intents = []
        sort_edge = dict(((name, []) for name in self._belongs.keys()))
        sort_counting = dict(((name, 0) for name in self._belongs.keys()))
        for dependency in self._dependencies:
            if 'left' not in dependency or 'right' not in dependency:
                raise GenerationError("attribute left/right missing")

            if 'dep' not in dependency or dependency['dep'] == 'before':  # OpX before OpY (default relation)
                sort_edge[dependency['left']].append(dependency['right'])
                sort_counting[dependency['right']] += 1
            elif dependency['dep'] == 'after':  # OpX after OpY
                sort_edge[dependency['right']].append(dependency['left'])
                sort_counting[dependency['left']] += 1
            else:
                raise GenerationError('unsupported dependency-type: ' + dependency['dep'])
        ready_erase = queue.Queue()
        for name, cnt in sort_counting.items():
            if cnt == 0:
                ready_erase.put(name)
        while ready_erase.qsize():
            name = ready_erase.get()
            sort_counting.pop(name)
            self._intents.extend(self._belongs[name])
            for node in sort_edge[name]:
                sort_counting[node] -= 1
                if sort_counting[node] == 0:
                    ready_erase.put(node)

        if len(sort_counting) == 0:
            return True
        self._intents = None
        return False

    def dictize(self):
        return {
            'intents': [
                json.dumps(tx.__dict__, sort_keys=True, indent=4, separators=(', ', ': ')) for tx in self.intents],
            'dependencies': self._dependencies
        }

    def purejson(self):
        return json.dumps(self.dictize(), sort_keys=True)

    def jsonize(self):
        return json.dumps(self.dictize(), sort_keys=True, indent=4, separators=(', ', ': '))

    def hash(self):
        return HexBytes(keccak(bytes(json.dumps(self.dictize(), sort_keys=True).encode(ENC)))).hex()


if __name__ == '__main__':
    intents_json = {
        "Op-intents": [
            {
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
            },
            {
                "name": "Op2",
                "op_type": "Payment",
                "dst": {
                    "domain": "Tendermint://chain2",
                    "user_name": "a2"
                },
                "src": {
                    "domain": "Ethereum://chain3",
                    "user_name": "a1"
                },
                "amount": 20,
                "unit": "iew"
            },
            {
                "op_type": "ContractInvocation",
                "name": "Op3",
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
        ],
        "dependencies": [{
            "left": "Op1",
            "right": "Op2",
            "dep": "after"
        }, {
            "left": "Op1",
            "right": "Op3",
            "dep": "after"
        }, {
            "left": "Op2",
            "right": "Op3",
            "dep": "after"
        }]
    }

    from uiputils.op_intents import OpIntent
    op_intents, owners = OpIntent.createopintents(intents_json['Op-intents'])
    print(op_intents, owners)

    tx_intents = TransactionIntents(op_intents, intents_json['dependencies'])

    print(tx_intents.__dict__)

    print(tx_intents.belongs)
    print(tx_intents.sort())
    print(*tx_intents.dictize()['intents'])
