
# python modules
from web3 import Web3

# uip modules
from uiputils.eth import FileLoad, JsonRPC
from uiputils.uiptypes import VerifiableExecutionSystem, DApp
from uiputils.cast import formated_json

# config
from uiputils.config import HTTP_HEADER
info_x = {
    'domain': "Ethereum://chain1",
    'name': "X",
    'passphrase': "123456"
}
info_y = {
    'domain': "Ethereum://chain2",
    'name': "Y",
    'passphrase': "123456"
}


def unlock_user(addr):
    unlock = JsonRPC.personal_unlock_account(addr, "123456", 20)
    response = JsonRPC.send(unlock, HTTP_HEADER, "http://127.0.0.1:8545")
    if not response['result']:
        raise ValueError("unlock failed. wrong password?")


if __name__ == '__main__':

    # prepare
    ves = VerifiableExecutionSystem()
    dapp_x = DApp(info_x)
    dapp_y = DApp(info_y)
    ves.appenduserlink([dapp_x, dapp_y])

    # load Sample.json
    op_intents_json = FileLoad.getopintents("opintents.json")

    session_content, isc, session_signature, tx_intents = ves.sessionSetupPrepare(op_intents_json)
    # print('session_content:', session_content)
    # print('session_signature:', session_signature)

    dapp_x.ackinit(ves, isc, session_content, session_signature)
    dapp_y.ackinit(ves, isc, session_content, session_signature)

    print(isc)

    print(isc.handle.handle.funcs())

    print("raw: ", ves.address)
    print(isc.handle.is_owner(ves.address))
    print(isc.handle.is_raw_sender(ves.address))
    print(isc.handle.is_owner(dapp_x.address))
    print(isc.handle.is_owner(dapp_y.address))
    print(isc.handle.tx_info_length())

    print(isc.handle.get_isc_state())
    # print(formated_json(ves.txs_pool[int(session_content[0])]['ack_dict']))

    on_chain_txs = [tx.jsonize() for tx in tx_intents.intents]

    print(on_chain_txs)

    for tx in on_chain_txs:
        unlock_user(tx['from'])
        tx_json = JsonRPC.eth_send_transaction(tx)
        print(JsonRPC.send(tx_json, HTTP_HEADER, "http://127.0.0.1:8545"))
