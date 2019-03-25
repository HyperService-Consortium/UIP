
from uiputils.eth.ethtypes import EthTransaction

if __name__ == '__main__':
    # chain_id, invoker, contract_address,
    # function_name, function_parameters = None, function_parameters_description = None,
    # gasuse = default_gasuse
    tx_intent = [
        'invoke',  # transaction_type
        "chain1",  # chain_id
        "0x7019fa779024c0a0eac1d8475733eefe10a49f3b",  # invoker
        "0x85854fe3853b7A51576bFd78564Ec1993f8820d1",  # address
        "isOwner",  # function name
        ["0x7019fa779024c0a0eac1d8475733eefe10a49f3b"],  # parameters
        ["address"]  # parameters_description
    ]
    tx = EthTransaction(*tx_intent)
    print(tx)
    print('function_sign ' + getattr(tx, 'signature'))
    print(tx.jsonize())

# function sign: 0x2f54bf6e
# 0x2f54bf6e000000000000000000000000ca35b7d915458ef540ade6068dfe2f44e8fa733c