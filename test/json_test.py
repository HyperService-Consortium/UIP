
# python modules
import json

# uip modules
from dapp import DApp
from uiputils.op_intents import OpIntent
from uiputils.transaction_intents import TransactionIntents

# eth modules
from uiputils.ethtools import FileLoad


if __name__ == '__main__':
    # load Sample.json
    op_intents_json = FileLoad.getopintents("opintents.json")

    # build eligible Op intents
    op_intents = OpIntent.createopintents(op_intents_json['Op-intents'])
    for op_intent in op_intents:
        print("---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----")
        print(json.dumps(op_intent.__dict__, sort_keys=True, indent=4, separators=(', ', ': ')))
        print("---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----")

    # Generate Transaction intents and Dependency Graph
    tx_intents = TransactionIntents(op_intents, op_intents_json['dependencies'])
    for tx_intent in tx_intents._intents:
        print("---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----")
        print("Transaction Chain-ID:", tx_intent.chain_host)
        print(
            "Transaction information:",
            json.dumps(tx_intent.jsonize(), sort_keys=True, indent=4, separators=(', ', ': '))
        )
        dappx = DApp(tx_intent.jsonize()['from'])
        print("---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----")

    with open('txintents.json', 'w') as tx_intents_file:
        tx_intents_file.write(tx_intents.jsonize())

'''Sample Output
---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
{
    "amount": 1000, 
    "dst": {
        "domain": "Ethereum://chain2", 
        "user_name": "Y"
    }, 
    "name": "Op1", 
    "op_type": "Payment", 
    "src": {
        "domain": "Ethereum://chain1", 
        "user_name": "X"
    }, 
    "unit": "wei"
}
---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
{
    "address": "0x85854fe3853b7A51576bFd78564Ec1993f8820d1", 
    "contract_domain": "Ethereum://chain1", 
    "func": "isOwner", 
    "invoker": "0xd051a43d3ea62afff3632bca3d5abf68bc6fd737", 
    "name": "Op2", 
    "op_type": "ContractInvocation", 
    "parameters": [
        "0x7019fa779024c0a0eac1d8475733eefe10a49f3b"
    ], 
    "parameters_description": [
        "address"
    ]
}
---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
Transaction Chain-ID: http://127.0.0.1:8545
Transaction information: {
    "from": "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e", 
    "gas": "0x493e0", 
    "to": "0x7019fa779024c0a0eac1d8475733eefe10a49f3b", 
    "value": "0x3e8"
}
---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
Transaction Chain-ID: http://127.0.0.1:8545
Transaction information: {
    "from": "0x91f030cfec606f9ff832aef20f768bf3a129b59c", 
    "gas": "0x493e0", 
    "to": "0xd051a43d3ea62afff3632bca3d5abf68bc6fd737", 
    "value": "0x3e8"
}
---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
Transaction Chain-ID: http://127.0.0.1:8545
Transaction information: {
    "data": "0x2f54bf6e0000000000000000000000007019fa779024c0a0eac1d8475733eefe10a49f3b", 
    "from": "0xd051a43d3ea62afff3632bca3d5abf68bc6fd737", 
    "gas": "0x493e0", 
    "to": "0x85854fe3853b7A51576bFd78564Ec1993f8820d1"
}
---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
'''
