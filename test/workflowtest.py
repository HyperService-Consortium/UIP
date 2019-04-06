
# python modules

# uip modules
from uiputils.ethtools import FileLoad, JsonRPC
from uiputils.ves import VerifiableExecutionSystem
from uiputils.dapp import DApp
from uiputils.nsb.nsb import EthLightNetStatusBlockChain
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

    session_content, isc, session_signature, tx_intents = ves.session_setup_prepare(op_intents_json)
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

    tx = on_chain_txs[0]
    atte = dapp_x.init_attestation(tx, StateType.inited, int(session_content[0]), 0)
    # update

    # relay
    atte_rec = dapp_x.receive(atte.encode())
    rlped_data = atte_rec.sign_and_encode()
    # update

    # check
    dapp_x.receive(rlped_data)

    # open
    unlock_user(tx['from'])
    tx_json = JsonRPC.eth_send_transaction(tx)
    print(JsonRPC.send(tx_json, HTTP_HEADER, "http://127.0.0.1:8545"))
    # verify_transaction_state?
    atte = dapp_x.init_attestation(tx, StateType.open, int(session_content[0]), 0)

    # relay(ves)
    dapp_x.receive(atte.encode())
    atte = dapp_x.init_attestation(tx, StateType.opened, int(session_content[0]), 0)

    # ves check
    dapp_x.receive(atte.encode())
    # close

    # relay
    tx = on_chain_txs[1]
    atte = dapp_y.init_attestation(tx, StateType.inited, int(session_content[0]), 1)
    # update

    # dapp_y
    atte_rec = dapp_y.receive(atte.encode())
    rlped_data = atte_rec.sign_and_encode()
    # update

    # relay(ves) check
    dapp_y.receive(rlped_data)

    # open
    unlock_user(tx['from'])
    tx_json = JsonRPC.eth_send_transaction(tx)
    print(JsonRPC.send(tx_json, HTTP_HEADER, "http://127.0.0.1:8545"))
    # verify_transaction_state?
    atte = dapp_y.init_attestation(tx, StateType.open, int(session_content[0]), 1)

    # dapp_y
    dapp_y.receive(atte.encode())
    atte = dapp_y.init_attestation(tx, StateType.opened, int(session_content[0]), 1)

    # dapp_y ckeck
    dapp_y.receive(atte.encode())
    # close

    # relay
    tx = on_chain_txs[2]
    atte = dapp_y.init_attestation(tx, StateType.inited, int(session_content[0]), 2)
    # update

    # dapp_y
    atte_rec = dapp_y.receive(atte.encode())
    rlped_data = atte_rec.sign_and_encode()
    # update

    # ves check
    dapp_y.receive(rlped_data)

    # open
    unlock_user(tx['from'])
    tx_json = JsonRPC.eth_send_transaction(tx)
    print(JsonRPC.send(tx_json, HTTP_HEADER, "http://127.0.0.1:8545"))
    # verify_transaction_state?
    atte = dapp_y.init_attestation(tx, StateType.open, int(session_content[0]), 1)

    # dapp_y
    dapp_y.receive(atte.encode())
    atte = dapp_y.init_attestation(tx, StateType.opened, int(session_content[0]), 1)

    # dapp_y ckeck
    dapp_y.receive(atte.encode())
    # close

    # settle

    # close
