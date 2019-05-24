
# python modules
import json
import time
import rlp

# uip modules
from uiputils.chain_dns import ChainDNS
from uiputils.uiptypes.attestation import Attestation
from uiputils.errors import VerificationError
from uiputils.transaction import StateType
from uiputils.nsb import EthLightNetStatusBlockChain
from uiputils.contract.wrapped_contract_function import ContractFunctionClient

# eth modules
from uiputils.ethtools import JsonRPC, SignatureVerifier

# ethereum modules
from web3 import Web3
from hexbytes import HexBytes
from eth_hash.auto import keccak


from py_nsbcli.system_action import SystemAction, Action

# config
from uiputils.config import HTTP_HEADER, action_using_flag

from uiputils.loggers import console_logger

# constant
ENC = 'utf-8'


class DApp:
    def __init__(self, user_info: dict):

        self.info = {}
        self.session_event = {}
        self.name = user_info['name']

        if 'accounts' not in user_info:
            if 'domain' not in user_info:
                raise KeyError("wrong format of user_info for creating DApp")
            chain_type, chain_id = user_info['domain'].split('://')
            chain_host = ChainDNS.gethost(chain_type, chain_id)
            self.info[chain_host] = self.info[user_info['domain']] = {
                'address': ChainDNS.checkuser(chain_type, chain_id, self.name),
                'host': chain_host,
                'domain': user_info['domain'],
                'password': None
            }
            if 'passphrase' in user_info:
                self.info[chain_host]['password'] = user_info['passphrase']
            self.default_domain = user_info['domain']
        else:
            if not hasattr(user_info, '__len__') or len(user_info['accounts']) == 0:
                raise KeyError("no valid info in user_info['accounts']")

            for infomation in user_info['accounts']:
                chain_type, chain_id = infomation['domain'].split('://')
                chain_host = ChainDNS.gethost(chain_type, chain_id)
                self.info[chain_host] = self.info[infomation['domain']] = {
                    'chain_type': chain_type,
                    'address': ChainDNS.checkuser(chain_type, chain_id, self.name),
                    'host': chain_host,
                    'domain': infomation['domain'],
                    'password': None
                }
                if 'passphrase' in infomation:
                    self.info[infomation['domain']]['password'] = infomation['passphrase']
            self.default_domain = user_info['accounts'][0]['domain']

    def unlockself(self, host_name=None):
        """
        assuming self.address is on Ethereum
        :param host_name:
        :return:
        """
        if host_name is None:
            host_name = self.default_domain

        host_info = self.info[host_name]

        if host_info['chain_type'] == 'Tendermint':
            return
        elif host_info['chain_type'] == 'Ethereum':
            unlock = JsonRPC.personal_unlock_account(host_info['address'], host_info['password'], 20)
            response = JsonRPC.send(unlock, HTTP_HEADER, host_info['host'])
            if not response['result']:
                raise ValueError("unlock failed. wrong password?")
        else:
            raise TypeError("unsupported chain-type: ", + host_info['chain_type'])

    def sign(self, msg, host_name=None):
        """
        assuming self.address is on Ethereum
        :param msg: msg to sign (bytes in string)
        :param host_name: that the msg will send to
        :return: signature
        """
        if host_name is None:
            host_name = self.default_domain

        host_info = self.info[host_name]

        if host_info['chain_type'] == 'Tendermint':
            if isinstance(msg, str):
                if msg[0:2] == "0x":
                    msg = msg[2:]
                msg = bytes.fromhex(msg)
            return host_info['password'].sign(msg)
        elif host_info['chain_type'] == 'Ethereum':
            self.unlockself(host_name)
            sign_json = JsonRPC.eth_sign(host_info['address'], msg)
            return JsonRPC.send(sign_json, HTTP_HEADER, host_info['host'])['result']
        else:
            raise TypeError("unsupported chain-type: ", + host_info['chain_type'])

    @staticmethod
    def call(trans):
        """
        call the contract_methods
        :param trans: transaction with contract invocation's information
        :return: results of function
        """
        if trans.chain_type == 'Ethereum':
            call_json = JsonRPC.eth_call(trans.jsonize())
            # print(json.dumps(tx_response, sort_keys=True, indent=4, separators=(', ', ': ')))
            return JsonRPC.send(call_json, HTTP_HEADER, trans.chain_host)['result']
        else:
            raise TypeError("unsupported chain-type: ", + trans.chain_type)

    def send(self, trans, passphrase=None):
        """
        transact the contract_methods
        :param trans: transaction with contract invocation's information
        :param passphrase:
        :return: None
        """
        if passphrase is None:
            passphrase = self.info[trans.chain_host]
        if trans.chain_type == 'Ethereum':
            unlock = JsonRPC.personal_unlock_account(self.info[trans.chain_host]['address'], passphrase, 20)
            tx_response = JsonRPC.send(unlock, HTTP_HEADER, trans.chain_host)
            print(json.dumps(tx_response, sort_keys=True, indent=4, separators=(', ', ': ')))

            packet_transaction = JsonRPC.eth_send_transaction(trans.jsonize())
            tx_response = JsonRPC.send(packet_transaction, HTTP_HEADER, trans.chain_host)
            print(json.dumps(tx_response, sort_keys=True, indent=4, separators=(', ', ': ')))

            tx_hash = tx_response['result']
            query = JsonRPC.eth_get_transaction_receipt(tx_hash)
            while True:
                tx_response = JsonRPC.send(query, HTTP_HEADER, trans.chain_host)
                if tx_response['result'] is None:
                    print("transacting")
                    time.sleep(2)
                    continue
                break
            print(json.dumps(tx_response, sort_keys=True, indent=4, separators=(', ', ': ')))
        else:
            raise TypeError("unsupported chain-type: ", + trans.chain_type)

    def ackinit(self, ves, isc, content, sig, host_name=None, testing=False):

        if host_name is None:
            host_name = self.default_domain
        host_info = self.info[host_name]
        host_name = host_info['domain']


        # if not SignatureVerifier.verify_by_raw_message(sig, rlp.encode(content), ves.address):
        #     # user refuse TODO
        #     try:
        #         ves.session_setup_update(int(content[0]), self.name, None)
        #     except Exception as e:
        #         raise e
        # user looking through content
        # print(sig, host_name)
        if host_name == "Tendermint://chain1":
            signature = self.sign(bytes.fromhex(sig[2:]), host_name)
        else:
            signature = self.sign(sig, host_name)

        console_logger.info(
            'dapp ({0}) is trying call user_ack, name: {1} host: {2}'.format(
                self.name,
                host_name,
                host_info
            )
        )
        if not testing:
            if host_name == "Tendermint://chain1":
                self.unlockself(host_name)
                sys_act = SystemAction(host_info['host'])
                sys_act.add_action(host_info['password'], Action(
                    bytes.fromhex("123456"), None, None,
                    action_using_flag[host_info['chain_type']].value, bytes.fromhex(sig[2:]),
                    signature
                ))
            else:
                self.unlockself(host_name)
                sys_act = SystemAction(host_info['host'])
                sys_act.add_action(host_info['password'], Action(
                    bytes.fromhex("123456"), None, None,
                    action_using_flag[host_info['chain_type']].value, bytes.fromhex(sig[2:]),
                    bytes.fromhex(signature[2:])
                ))

        # what if update no successful? TODO

        ret = ves.session_setup_update(int(content[0]), host_name + '.' + self.name, signature)
        if isinstance(ret, Exception):
            raise ret
        else:
            console_logger.info('dapp ({0}) user_ack accepted by ves: {1}'.format(self.name, ves.address))
            self.session_event[int(content[0])] = {
                'host_info': host_info,
                # TODO: temporary eth-nsb-address
                'isc': isc.address,
                'nsb': "PLACEHODER"
            }

    def receive(self, rlped_atte, session_id, tid, aid, host_name=None) -> Attestation:

        if host_name is None:
            host_name = self.default_domain
        host_info = self.info[host_name]
        host_name = host_info['domain']

        try:
            if session_id not in self.session_event:
                raise KeyError("No such session_id" + str(session_id))

            # session_info = self.session_event[session_id]
            # nsb = EthLightNetStatusBlockChain(
            #     session_info['host_info']['address'],
            #     session_info['host_info']['host'],
            #     session_info['nsb']
            # )
            sys_act = SystemAction(host_info['host'])

            atte = Attestation(rlped_atte)
            print(sys_act.get_action(host_info['password'], bytes.fromhex("123456"), tid, aid))
            # if not nsb.validate_action(msghash=atte.pre_hash, signature=atte.signatures[-1][0]):
            #     raise VerificationError("this action is not on nsb")

        except VerificationError as e:
            # TODO: stop ISC ?
            raise e

        return atte

    def sign_attestation(self, atte: Attestation, host_name: str = None) -> bytes:
        if host_name is None:
            host_name = self.default_domain
        return atte.sign_and_encode([
            self.sign(HexBytes(atte.hash).hex()),
            self.info[host_name]['address']
        ])

    def init_attestation(
            self, onchain_tx: dict,
            state: StateType,
            session_index: int,
            tx_index: int,
            host_name: str = None
    ) -> Attestation:
        if host_name is None:
            host_name = self.default_domain
        content_list = [
            json.dumps(
                onchain_tx,
                sort_keys=True
            ).encode(ENC),
            HexBytes(state.value),
            HexBytes(session_index),
            HexBytes(tx_index)
        ]
        return Attestation.create_attestation(
            content_list,
            [
                self.sign(HexBytes(keccak(rlp.encode([content_list, []]))).hex(), host_name),
                self.info[host_name]['address']
            ]
        )

    def send_attestation(
            self,
            session_index: int,
            atte: Attestation,
            tx_index: int, state: StateType,
            host_name: str = None
    ) -> ContractFunctionClient:
        if host_name is None:
            host_name = self.default_domain
        host_info = self.info[host_name]
        # nsb = EthLightNetStatusBlockChain(
        #     host_info['address'],
        #     host_info['host'],
        #     self.session_event[session_index]['nsb']
        # )

        console_logger.info(
            'dapp ({0}) adding atte[\n'
            '     isc: {1}\n'
            '    transaction-action index: ({2}, {3})\n'
            '    atte: ({4}, {5})\n'
            ']'.format(
                self.name, self.session_event[session_index]['isc'], tx_index, state.value,
                HexBytes(atte.pre_hash).hex(), atte.signatures[-1][0].to_hex()
            )
        )
        self.unlockself(host_name)
        sys_act = SystemAction(host_info['host'])
        sys_act.add_action(host_info['password'], Action(
            bytes.fromhex("123456"), tx_index, state.value,
            action_using_flag[host_info['chain_type']].value, HexBytes(atte.pre_hash),
            atte.signatures[-1][0].bytes()
        ))
        # return nsb.add_action_proposal(
        #     self.session_event[session_index]['isc'],
        #     tx_index,
        #     state.value,
        #     atte.pre_hash,
        #     atte.signatures[-1][0].to_hex()
        # )

# aborted code
# user ack:
# from hexbytes import HexBytes
# vesack = HexBytes(isc.handle.vesack()).hex()
# print(HexBytes(isc.handle.vesack()).hex())

# print(SignatureVerifier.verify_by_hashed_message(signatrue, vesack, self.address))
