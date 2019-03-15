
from uiputils.eth import FileLoad
from uiputils.uiptypes import createopintents
if __name__ == '__main__':
    op_intents_json = FileLoad.getopintents("opintents.json")
    # print(op_intent_json)

    op_intents = createopintents(op_intents_json)
    print(op_intents)
    # for op_intent in op_intents:
    #     op_intent_dict = op_intent.__dict__
    #     for k, v in op_intent_dict.items():
    #         print(k + ": ", v)
    #     print("----------------------------------")
