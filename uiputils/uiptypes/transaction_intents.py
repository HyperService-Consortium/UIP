import json

from eth_hash.auto import keccak
from hexbytes import HexBytes

from uiputils.uiptypes import ChainDNS
from uiputils.eth.ethtypes import EthTransaction as EthTx
from uiputils.uiperror import GenerationError


ENC = 'utf-8'


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