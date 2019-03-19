
from uiputils.eth import FileLoad
from uiputils.uiptypes import VerifiableExecutionSystem, DApp, ChainDNS

#config
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

    session_content, session_signature = ves.sessionSetupPrepare(op_intents_json)
    print('session_content:', session_content)
    print('session_signature:', session_signature)

    # print(tx_intents.intents)
