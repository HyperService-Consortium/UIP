
from uiputils.ethtools import JsonRPC
from uiputils.nsb.nsb import EthLightNetStatusBlockChain

from uiputils.config import HTTP_HEADER


def unlockself(address, password, chain_host):
    unlock = JsonRPC.personal_unlock_account(address, password, 20)
    response = JsonRPC.send(unlock, HTTP_HEADER, chain_host)
    if not response['result']:
        raise ValueError("unlock failed. wrong password?")


if __name__ == '__main__':
    light_nsb = EthLightNetStatusBlockChain(
        '0x7019fa779024c0a0eac1d8475733eefe10a49f3b',
        'http://127.0.0.1:8545',
        '0x4f358c8e9b891082eb61fb96f1a0cbdf23c14b6b'
    )

    unlockself('0x7019fa779024c0a0eac1d8475733eefe10a49f3b', "123456", 'http://127.0.0.1:8545')
    lazyfunc = light_nsb.add_transaction_proposal('0x7019fa779024c0a0eac1d8475733eefe10a49f3b', 15)
    print(lazyfunc)
    lazyfunc.transact()
    print(lazyfunc.loop_and_wait())

    lazyfunc = light_nsb.is_active_isc('0x7019fa779024c0a0eac1d8475733eefe10a49f3b')
    print(lazyfunc)
    print(lazyfunc.call())
