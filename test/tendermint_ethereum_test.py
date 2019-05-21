
# python modules

# uip modules
from uiputils.ethtools import FileLoad, JsonRPC
from uiputils.ves import VerifiableExecutionSystem
from uiputils.dapp import DApp
from uiputils.transaction import StateType

from py_nsbcli.types import LevelDB
from py_nsbcli import KVDB


# config
from uiputils.config import HTTP_HEADER

from uiputils.loggers import console_logger


kvdb_dir = "E:/project/go/src/github.com/Myriad-Dreamin/NSB/bin/kvstore"

kvdb = KVDB(LevelDB(kvdb_dir))
alice = kvdb.load_wallet("Alice")

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
        {'domain': "Ethereum://chain1",
         'passphrase': "123456"}
    ]
}

enc_info_x = {
    'domain': "http://127.0.0.1:8545",
    'name': "0xd051a43d3ea62afff3632bca3d5abf68bc6fd737",
    'passphrase': "123456"
}

info_y = {
    'name': "a2",
    'accounts': [
        {'domain': "Tendermint://chain1",
         'passphrase': alice},
        {'domain': "Ethereum://chain1",
         'passphrase': "123456"}
    ]
}

enc_info_y = {
    'domain': "http://47.254.66.11:26657",
    'name': "0xcfe900c7a56f87882f0e18e26851bce7b7e61ebeca6c4b235fa360d627dfac63",
    'passphrase': alice
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


def temporary_transact(tx, host):

    if host == "http://47.254.66.11:26657":
        from py_nsbcli import Client, Admin
        from py_nsbcli.system_token import SystemToken
        from hexbytes import HexBytes
        admin = Admin()
        admin.set_rpc_host(host)
        cli = Client(admin)
        token_cli = SystemToken(cli)

        token_cli.transfer(alice, HexBytes(tx['dst']), tx['fund'])
    else:
        tx_json = JsonRPC.eth_send_transaction(tx)
        print(tx)
        print(JsonRPC.send(tx_json, HTTP_HEADER, host))


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
    op_intents_json = FileLoad.getopintents("./opintents3.json")

    # for intent in op_intents_json['Op-intents']:
    #     intent['contract_domain'] = "Ethereum://" + intent['contract_domain']

    session_content, isc, session_signature, tx_intents = ves.session_setup_prepare(op_intents_json)

    dapp_x.ackinit(ves, isc, session_content, session_signature, ves.chain_host, testing=False)
    dapp_y.ackinit(ves, isc, session_content, session_signature, ves.chain_host, testing=False)

    print("raw: ", ves.address)
    print(isc.is_owner(ves.address))
    print(isc.is_raw_sender(ves.address))
    print(isc.is_owner(dapp_x.info[ves.chain_host]['address']))
    print(isc.is_owner(dapp_y.info[ves.chain_host]['address']))
    print(isc.tx_info_length())
    print(isc.get_isc_state())
    print(ves.nsb.is_active_isc(isc.address))

    user_table = [
        (dapp_y, ves),
        (ves, dapp_x),
        (dapp_x, ves)
    ]
    session_id = int(session_content[0])

    for idx, [u, v] in enumerate(user_table):
        # assert tx_intent is on ISC

        # Part_A # inited ##############################################################################################

        # compute on_chain_tx
        tx = tx_intents.intents[idx].jsonize()
        console_logger.info('on chain transaction computed index: {0}, content: {1}'.format(idx, tx))

        # compute attestation
        atte = u.init_attestation(tx, StateType.inited, session_id, idx, ves.chain_host)

        # send inited attestaion
        laz_func = u.send_attestation(session_id, atte, idx, StateType.inited, ves.chain_host)
        u.unlockself(ves.chain_host)
        laz_func.transact()
        console_logger.info('nsb received action, response: {}'.format(laz_func.loop_and_wait()))

        # Part_Z # open ################################################################################################

        # receive attestaion
        atte_rec = v.receive(atte.encode(), int(session_content[0]))

        # compute attestation
        rlped_data = v.sign_attestation(atte_rec)

        # send open-request attestion
        laz_func = v.send_attestation(session_id, atte_rec, idx, StateType.open, ves.chain_host)
        v.unlockself(ves.chain_host)
        laz_func.transact()
        console_logger.info('nsb received action, response: {}'.format(laz_func.loop_and_wait()))

        # Part_A # opened ##############################################################################################

        # no necessary to ack, just verify it
        u.receive(rlped_data, int(session_content[0]))

        # open transaction
        u.unlockself(tx_intents.intents[idx].chain_host)
        temporary_transact(tx, tx_intents.intents[idx].chain_host)

        # verify_transaction_state?

        # compute opened attestaion
        atte = u.init_attestation(tx, StateType.opened, int(session_content[0]), 0, ves.chain_host)
        laz_func = u.send_attestation(session_id, atte, idx, StateType.opened, ves.chain_host)
        laz_func.transact()
        console_logger.info('nsb received action, response: {}'.format(laz_func.loop_and_wait()))

        # Part_Z # closed ##############################################################################################

        # no necessary to ack, just verify it
        v.receive(atte.encode(), int(session_content[0]))

        atte = v.init_attestation(tx, StateType.closed, int(session_content[0]), 0, ves.chain_host)
        laz_func = v.send_attestation(session_id, atte, idx, StateType.closed, ves.chain_host)
        laz_func.transact()
        console_logger.info('nsb received action, response: {}'.format(laz_func.loop_and_wait()))

        # end ##########################################################################################################

        u.receive(atte.encode(), int(session_content[0]))
    # #
    # # # settle
    # #
    # # # close

# user_ack
# {"from": eth.coinbase, "to":"0x137db188135379e419d796dc380f3825d3d6f2bb", "data":"0x8589ee50"}
