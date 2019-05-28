
# python modules

# uip modules
from uiputils.ethtools import FileLoad, JsonRPC
from ves import VerifiableExecutionSystem
from dapp import DApp
from uiputils.transaction import StateType
import time


# config
from uiputils.config import HTTP_HEADER, alice, bob, tom

from uiputils.loggers import console_logger

from py_nsbcli.modules.admin import set_admin_singleton_mode
set_admin_singleton_mode(False)
# # Only one contract is involved in this dApp
#
# import "asset.sol"
#
# account a1 = EthereumX::Account(0x...)
# account a2 = Tendermint::Account(0x...,)
# contract c1 = EthereumX::CryptoAsset(0x...)
#
# op op1 payment 20 XYZ from a2 to a1 with 1 XYZ as 0.5 ether # this defines the token exchange rate
# op op2 invocation c1.deposit(10) using a1
#
# op1 before op2

info_x = {
    'name': "a1",
    'accounts': [
        {'domain': "Ethereum://chain3",
         'passphrase': "123456"},
        {'domain': "Tendermint://chain1",
         'passphrase': bob}
    ]
}

info_y = {
    'name': "a2",
    'accounts': [
        {'domain': "Tendermint://chain1",
         'passphrase': alice},
        {'domain': "Tendermint://chain2",
         'passphrase': tom}
    ]
}


def unlock_user(user):
    unlock = JsonRPC.personal_unlock_account(user['name'], user['passphrase'], 20)
    response = JsonRPC.send(unlock, HTTP_HEADER, user['domain'])
    if not response['result']:
        raise ValueError("unlock failed. wrong password?")


def temporary_transact(tx, host):

    if host == "http://47.251.2.73:26657":
        from py_nsbcli import Client, Admin
        admin = Admin()
        admin.set_rpc_host(host)
        cli = Client(admin)
        from contract.tendermint.delegate.contract import DelegateContract
        opt = DelegateContract(cli)
        print(opt.vote(tom, bytes.fromhex(tx['dst'][2:])))
    else:
        tx_json = JsonRPC.eth_send_transaction(tx)
        print(tx)
        resp = JsonRPC.send(tx_json, HTTP_HEADER, host)['result']
        get_tx = JsonRPC.eth_get_transaction_receipt(resp)
        while True:
            response = JsonRPC.send(get_tx, HTTP_HEADER, host)
            print("result", response)
            break
            # if response['result'] is None:
            #     print("Exec...", resp)
            #     time.sleep(5)


if __name__ == '__main__':
    # 029a
    tot_time = time.perf_counter()
    # prepare
    ves = VerifiableExecutionSystem()
    dapp_x = DApp(info_x)
    dapp_y = DApp(info_y)
    ves.appenduserlink([dapp_x, dapp_y])

    console_logger.info('{0} built, info:{1}'.format(dapp_x, dapp_x.info))
    console_logger.info('{0} built, info:{1}'.format(dapp_y, dapp_y.info))
    console_logger.info('{0} built, info:{1}'.format(ves, ves.__dict__))

    # load Sample.json
    op_intents_json = FileLoad.getopintents("./opintents5.json")

    # for intent in op_intents_json['Op-intents']:
    #     intent['contract_domain'] = "Ethereum://" + intent['contract_domain']

    session_content, isc, session_signature, tx_intents = ves.session_setup_prepare(op_intents_json)

    dapp_x.ackinit(ves, isc, session_content, session_signature, ves.nsb.host, testing=False)
    dapp_y.ackinit(ves, isc, session_content, session_signature, ves.nsb.host, testing=False)

    # print("raw: ", ves.address)
    # print(isc.is_owner(ves.address))
    # print(isc.is_raw_sender(ves.address))
    # print(isc.is_owner(dapp_x.info[ves.nsb.host]['address']))
    # print(isc.is_owner(dapp_y.info[ves.nsb.host]['address']))
    # print(isc.tx_info_length())
    # print(isc.get_isc_state())
    # print(ves.nsb.is_active_isc(isc.address))

    user_table = [
        (dapp_y, ves),
        (dapp_x, ves)
    ]
    session_id = int(session_content[0])

    tag_time = None
    tag_time_end = None
    print("prepare end..", time.perf_counter() - tot_time)
    for idx, [u, v] in enumerate(user_table):
        # assert tx_intent is on ISC

        # Part_A # inited ##############################################################################################

        print("compute on_chain_tx")
        tag_time = time.perf_counter()
        # compute on_chain_tx
        tx = tx_intents.intents[idx].jsonize()
        console_logger.info('on chain transaction computed index: {0}, content: {1}'.format(idx, tx))
        tag_time_end = time.perf_counter() - tag_time
        print("compute on_chain_tx", tag_time_end)
        print("attestation inited")
        tag_time = time.perf_counter()
        # compute attestation
        atte = u.init_attestation(tx, StateType.inited, session_id, idx, ves.nsb.host)

        # send inited attestaion
        ret = u.send_attestation(session_id, atte, idx, StateType.inited, ves.nsb.host)

        # receive attestaion
        atte_rec = v.receive(atte.encode(), int(session_content[0]), idx, StateType.inited.value, ves.nsb.host)

        tag_time_end = time.perf_counter() - tag_time
        print("attestation inited", tag_time_end)
        # laz_func = u.send_attestation(session_id, atte, idx, StateType.inited, ves.nsb.host)
        # u.unlockself(ves.nsb.host)
        # laz_func.transact()
        # console_logger.info('nsb received action, response: {}'.format(laz_func.loop_and_wait()))
        console_logger.info('nsb received action, response: {}'.format(ret))

        # Part_Z # open ################################################################################################

        print("attestation open")
        tag_time = time.perf_counter()
        # compute attestation
        rlped_data = v.sign_attestation(atte_rec)

        # send open-request attestion
        ret = v.send_attestation(session_id, atte_rec, idx, StateType.open, ves.nsb.host)

        # no necessary to ack, just verify it
        u.receive(rlped_data, int(session_content[0]), idx, StateType.open.value, ves.nsb.host)

        tag_time_end = time.perf_counter() - tag_time
        print("attestation open", tag_time_end)
        # laz_func = v.send_attestation(session_id, atte_rec, idx, StateType.open, ves.nsb.host)
        # v.unlockself(ves.nsb.host)
        # laz_func.transact()
        # console_logger.info('nsb received action, response: {}'.format(laz_func.loop_and_wait()))
        console_logger.info('nsb received action, response: {}'.format(ret))

        # Part_A # opened ##############################################################################################

        # open transaction
        print("transact")
        tag_time = time.perf_counter()

        u.unlockself(tx_intents.intents[idx].chain_host)
        temporary_transact(tx, tx_intents.intents[idx].chain_host)

        tag_time_end = time.perf_counter() - tag_time
        print("transact", tag_time_end)

        # verify_transaction_state?

        print("attestation opened")
        tag_time = time.perf_counter()
        # compute opened attestaion
        atte = u.init_attestation(tx, StateType.opened, int(session_content[0]), 0, ves.nsb.host)

        # send opened attestion
        ret = u.send_attestation(session_id, atte, idx, StateType.opened, ves.nsb.host)

        # no necessary to ack, just verify it
        v.receive(atte.encode(), int(session_content[0]), idx, StateType.opened.value, ves.nsb.host)

        tag_time_end = time.perf_counter() - tag_time
        print("attestation opened", tag_time_end)

        # laz_func = u.send_attestation(session_id, atte, idx, StateType.opened, ves.nsb.host)
        # laz_func.transact()
        # console_logger.info('nsb received action, response: {}'.format(laz_func.loop_and_wait()))
        console_logger.info('nsb received action, response: {}'.format(ret))

        # Part_Z # closed ##############################################################################################

        # atte = v.init_attestation(tx, StateType.closed, int(session_content[0]), 0, ves.nsb.host)
        # laz_func = v.send_attestation(session_id, atte, idx, StateType.closed, ves.nsb.host)
        # laz_func.transact()
        # console_logger.info('nsb received action, response: {}'.format(laz_func.loop_and_wait()))

        # compute closed attestaion
        print("attestation closed")
        tag_time = time.perf_counter()
        atte = v.init_attestation(tx, StateType.closed, int(session_content[0]), 0, ves.nsb.host)
        # send closed attestion
        ret = v.send_attestation(session_id, atte, idx, StateType.closed, ves.nsb.host)

        # receive closed attestion
        u.receive(atte.encode(), int(session_content[0]), idx, StateType.closed.value, ves.nsb.host)

        tag_time_end = time.perf_counter() - tag_time
        print("attestation closed", tag_time_end)
        console_logger.info('nsb received action, response: {}'.format(ret))

        # end ##########################################################################################################

        print("----------end transaction----------")
    # #
    # # # settle
    # #
    # # # close
    print("tot_time", time.perf_counter() - tot_time)

# user_ack
# {"from": eth.coinbase, "to":"0x137db188135379e419d796dc380f3825d3d6f2bb", "data":"0x8589ee50"}
