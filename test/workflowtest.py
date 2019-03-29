
# python modules
from web3 import Web3

# uip modules
from uiputils.eth import FileLoad
from uiputils.uiptypes import VerifiableExecutionSystem, DApp
from uiputils.cast import formated_json

# config
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


if __name__ == '__main__':

    # prepare
    ves = VerifiableExecutionSystem()
    dapp_x = DApp(info_x)
    dapp_y = DApp(info_y)
    ves.appenduserlink([dapp_x, dapp_y])

    # load Sample.json
    op_intents_json = FileLoad.getopintents("opintents.json")

    session_content, isc, session_signature = ves.sessionSetupPrepare(op_intents_json)
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

    # print(tx_intents.intents)
