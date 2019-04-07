
# python modules

# uip modules
from uiputils.ethtools import FileLoad, JsonRPC
from uiputils.ves import VerifiableExecutionSystem
from uiputils.dapp import DApp
from uiputils.chain_dns import ChainDNS
from uiputils.transaction import StateType

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

info_relay_x = {
    'domain': "Ethereum://chain1",
    'name': "relay_nsb",
    'passphrase': "123456"
}

info_relay_y = {
    'domain': "Ethereum://chain2",
    'name': "relay_nsb",
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
    relay_x = DApp(info_relay_x)
    relay_y = DApp(info_relay_y)
    ves.appenduserlink([dapp_x, dapp_y])

    # load Sample.json
    op_intents_json = FileLoad.getopintents("opintents.json")

    session_content, isc, session_signature, tx_intents = ves.session_setup_prepare(op_intents_json)
    # print('session_content:', session_content)
    # print('session_signature:', session_signature)

    dapp_x.ackinit(ves, isc, session_content, session_signature)
    dapp_y.ackinit(ves, isc, session_content, session_signature)

    print(isc)

    # print(isc.handle.handle.funcs())
    #
    # print("raw: ", ves.address)
    # print(isc.handle.is_owner(ves.address))
    # print(isc.handle.is_raw_sender(ves.address))
    # print(isc.handle.is_owner(dapp_x.address))
    # print(isc.handle.is_owner(dapp_y.address))
    # print(isc.handle.tx_info_length())

    print(isc.handle.get_isc_state())
    # print(formated_json(ves.txs_pool[int(session_content[0])]['ack_dict']))

    on_chain_txs = [tx.jsonize() for tx in tx_intents.intents]

    print(on_chain_txs)

    user_table = [
        (dapp_x, relay_x),
        (relay_y, dapp_y),
        (dapp_y, ves)
    ]

    for idx, [u, v] in enumerate(user_table):
        # assert tx_intent is on ISC

        # compute on_chan_tx
        tx = tx_intents.intents[idx].jsonize()
        print(tx)
        atte = u.init_attestation(tx, StateType.inited, int(session_content[0]), 0)
        # update

        # relay
        atte_rec = v.receive(atte.encode())
        rlped_data = v.sign_attestation(atte_rec)
        # update

        # check
        u.receive(rlped_data)

        # open
        unlock_user(tx['from'])
        tx_json = JsonRPC.eth_send_transaction(tx)
        print(JsonRPC.send(tx_json, HTTP_HEADER, tx_intents.intents[idx].chain_host))
        # verify_transaction_state?
        atte = u.init_attestation(tx, StateType.open, int(session_content[0]), 0)

        #
        v.receive(atte.encode())
        atte = v.init_attestation(tx, StateType.opened, int(session_content[0]), 0)

        # ves check
        ves.receive(atte.encode())
        # close

    #
    # # settle
    #
    # # close
