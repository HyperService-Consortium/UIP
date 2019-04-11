
# python modules

# uip modules
from uiputils.ethtools import FileLoad, JsonRPC
from uiputils.ves import VerifiableExecutionSystem
from uiputils.dapp import DApp
from uiputils.transaction import StateType


# config
from uiputils.config import HTTP_HEADER

from uiputils.config import console_logger

info_x = {
    'name': "a1",
    'accounts': [
        {'domain': "Ethereum://Chain1",
         'passphrase': "123456"}
    ]
}
enc_info_x = {
    'domain': "http://127.0.0.1:8545",
    'name': "0x7019fa779024c0a0eac1d8475733eefe10a49f3b",
    'passphrase': "123456"
}
info_y = {
    'name': "a2",
    'accounts': [
        {'domain': "Ethereum://BuptChain1",
         'passphrase': "123456"},
        {'domain': "Ethereum://Chain1",
         'passphrase': "123456"}
    ]
}
enc_info_y = {
    'domain': "http://162.105.87.118:8545",
    'name': "0xf4dacff5eba7426295e27a32d389fff3cde55de2",
    'passphrase': "123456"
}
enc_info_relay_y = {
    'domain': "http://127.0.0.1:8545",
    'name': "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e",
    'passphrase': "123456"
}


def unlock_user(user):
    unlock = JsonRPC.personal_unlock_account(user['name'], user['passphrase'], 20)
    response = JsonRPC.send(unlock, HTTP_HEADER, user['domain'])
    if not response['result']:
        raise ValueError("unlock failed. wrong password?")


if __name__ == '__main__':

    # prepare
    ves = VerifiableExecutionSystem()
    dapp_x = DApp(info_x)
    dapp_y = DApp(info_y)
    ves.appenduserlink([dapp_x, dapp_y])

    console_logger.info('{0} built, info:{1}'.format(dapp_x, dapp_x.info))
    console_logger.info('{0} built, info:{1}'.format(dapp_y, dapp_y.info))
    console_logger.info('{0} built, info:{1}'.format(ves, ves.__dict__))

    # load Sample.json
    op_intents_json = FileLoad.getopintents("./opintents2.json")

    for intent in op_intents_json['Op-intents']:
        intent['contract_domain'] = "Ethereum://" + intent['contract_domain']

    session_content, isc, session_signature, tx_intents = ves.session_setup_prepare(op_intents_json)

    console_logger.info('ves created session:{}'.format(ves.txs_pool[1]))
    # print(session_content, isc, session_signature, tx_intents)
    # # # print('session_content:', session_content)
    # # # print('session_signature:', session_signature)
    #
    # dapp_x.ackinit(ves, isc, session_content, session_signature, ves.chain_host)
    # dapp_y.ackinit(ves, isc, session_content, session_signature, ves.chain_host)
    #
    # print(isc.handle.handle.funcs())
    #
    # print("raw: ", ves.address)
    # print(isc.handle.is_owner(ves.address))
    # print(isc.handle.is_raw_sender(ves.address))
    # print(isc.handle.is_owner(dapp_x.info[ves.chain_host]['address']))
    # print(isc.handle.is_owner(dapp_y.info[ves.chain_host]['address']))
    # print(isc.handle.tx_info_length())
    # print(isc)
    # print(isc.__dict__)
    # print(isc.handle.get_isc_state())

    # # print(formated_json(ves.txs_pool[int(session_content[0])]['ack_dict']))
    #
    # on_chain_txs = [tx.jsonize() for tx in tx_intents.intents]
    #
    # print(on_chain_txs)
    #
    # user_table = [
    #     (dapp_x, ves),
    #     (dapp_y, ves)
    # ]
    #
    # unlock_table = [
    #     enc_info_x,
    #     enc_info_y
    # ]
    #
    # for idx, [u, v] in enumerate(user_table):
    #     # assert tx_intent is on ISC
    #
    #     # compute on_chan_tx
    #     tx = tx_intents.intents[idx].jsonize()
    #     print(tx)
    #     atte = u.init_attestation(tx, StateType.inited, int(session_content[0]), 0)
    #     # update
    #
    #     # relay
    #     atte_rec = v.receive(atte.encode())
    #     rlped_data = v.sign_attestation(atte_rec)
    #     # update
    #
    #     # check
    #     u.receive(rlped_data)
    #
    #     # open
    #     unlock_user(tx['from'])
    #     tx_json = JsonRPC.eth_send_transaction(tx)
    #     print(JsonRPC.send(tx_json, HTTP_HEADER, tx_intents.intents[idx].chain_host))
    #     # verify_transaction_state?
    #     atte = u.init_attestation(tx, StateType.open, int(session_content[0]), 0)
    #
    #     #
    #     v.receive(atte.encode())
    #     atte = v.init_attestation(tx, StateType.opened, int(session_content[0]), 0)
    #
    #     # ves check
    #     ves.receive(atte.encode())
    #     # close
    #
    # #
    # # # settle
    # #
    # # # close

# user_ack
# {"from": eth.coinbase, "to":"0x137db188135379e419d796dc380f3825d3d6f2bb", "data":"0x8589ee50"}
