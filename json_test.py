
from uiputils.eth import FileLoad
from uiputils.uiptypes import createopintents, TransactionIntent
if __name__ == '__main__':
    op_intents_json = FileLoad.getopintents("opintents.json")
    # print(op_intent_json)

    op_intents = createopintents(op_intents_json['Op-intents'])
    # print(op_intents)
    # for op_intent in op_intents:
    #     op_intent_dict = op_intent.__dict__
    #     for k, v in op_intent_dict.items():
    #         print(k + ": ", v)
    #     print("----------------------------------")
    tx_intent = TransactionIntent(op_intents, op_intents_json['dependencies'])

    with open('txintents.json', 'w') as tx_intent_file:
        tx_intent_file.write(tx_intent.jsonize())
