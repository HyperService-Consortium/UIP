
# python modules
import json
import time
import rlp

# uip modules
from uiputils.chain_dns import ChainDNS
from uiputils.uiptypes.attestation import Attestation
from uiputils.errors import VerificationError
from uiputils.transaction import StateType

# eth modules
from uiputils.ethtools import JsonRPC, SignatureVerifier

# ethereum modules
from web3 import Web3
from hexbytes import HexBytes
from eth_hash.auto import keccak

# config
from uiputils.config import HTTP_HEADER

# constant
ENC = 'utf-8'


class DApp:
    def __init__(self, user_info: dict):

        self.info = {}
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
        unlock = JsonRPC.personal_unlock_account(host_info['address'], host_info['password'], 20)
        response = JsonRPC.send(unlock, HTTP_HEADER, host_info['host'])
        if not response['result']:
            raise ValueError("unlock failed. wrong password?")

    def sign(self, msg, host_name=None):
        """
        assuming self.address is on Ethereum
        :param msg: msg to sign (bytes in string)
        :param host_name: that the msg will send to
        :return: signature
        """
        if host_name is None:
            host_name = self.default_domain
        self.unlockself(host_name)
        host_info = self.info[host_name]
        sign_json = JsonRPC.eth_sign(host_info['address'], msg)
        return JsonRPC.send(sign_json, HTTP_HEADER, host_info['host'])['result']

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

    def ackinit(self, ves, isc, content, sig, host_name=None):
        if host_name is None:
            host_name = self.default_domain
        host_info = self.info[host_name]
        host_name = host_info['domain']
        if not SignatureVerifier.verify_by_raw_message(sig, rlp.encode(content), ves.address):
            # not try but here ... TODO
            try:
                ves.session_setup_update(int(content[0]), self.name, None)
            except Exception as e:
                raise e
        # look through content

        # from hexbytes import HexBytes
        # vesack = HexBytes(isc.handle.vesack()).hex()
        # print(HexBytes(isc.handle.vesack()).hex())

        signatrue = self.sign(sig)

        # print(SignatureVerifier.verify_by_hashed_message(signatrue, vesack, self.address))

        self.unlockself(host_name)
        ack_func = isc.handle.user_ack(signatrue, {
            'from': Web3.toChecksumAddress(host_info['address']),
            'gas': hex(5000000)
        })
        ack_func.transact()
        print(ack_func.loop_and_wait())

        # not try but here ... TODO
        ret = ves.session_setup_update(int(content[0]), host_name + '.' + self.name, signatrue)
        if isinstance(ret, Exception):
            raise ret
        else:
            print("success")

    @staticmethod
    def receive(rlped_atte) -> Attestation:
        try:
            # TODO: verify attestation is on the nsb
            atte = Attestation(rlped_atte)
        except VerificationError as e:
            # TODO: stop ISC ?
            raise e

        return atte

    def sign_attestation(self, atte: Attestation, host_name: str = None) -> bytes:
        if host_name is None:
            host_name = self.default_domain
        return atte.sign_and_encode([
            self.sign(HexBytes(atte.hash()).hex()),
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
                self.sign(HexBytes(keccak(rlp.encode([content_list, []]))).hex()),
                self.info[host_name]['address']
            ]
        )
