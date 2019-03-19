
import json

from uiputils.eth import FileLoad
from uiputils.uiptypes import DApp, createopintents, TransactionIntents


if __name__ == '__main__':
    op_intents_json = FileLoad.getopintents("opintents.json")
    # print(op_intent_json)

    op_intents = createopintents(op_intents_json['Op-intents'])
    print(op_intents)
    for op_intent in op_intents:
        op_intent_dict = op_intent.__dict__
        for k, v in op_intent_dict.items():
            print(k + ": ", v)
        print("----------------------------------")
    tx_intents = TransactionIntents(op_intents, op_intents_json['dependencies'])

    with open('txintents.json', 'w') as tx_intents_file:
        tx_intents_file.write(tx_intents.jsonize())
    idx = 0
    for tx_intent in tx_intents.intents:
        idx += 1
        print(tx_intent.chain_host)
        print(json.dumps(tx_intent.jsonize(), sort_keys=True, indent=4, separators=(', ', ': ')))
        dappx = DApp(tx_intent.jsonize()['from'])
        if idx != 3:
            continue
            # dappx.send(tx_intent, "123456")
        else:
            dappx.call(tx_intent)

# 0x2f54bf6e0000000000000000000000007019fa779024c0a0eac1d8475733eefe10a49f3b
# 0x2f54bf6e000000000000000000000000ca35b7d915458ef540ade6068dfe2f44e8fa733c