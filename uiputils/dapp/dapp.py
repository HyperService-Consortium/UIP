
# python modules
import json
import time
import rlp

# uip modules
from uiputils.chain_dns import ChainDNS

# eth modules
from uiputils.ethtools import JsonRPC, SignatureVerifier

# config
from uiputils.config import HTTP_HEADER


class DApp:
    def __init__(self, user_loc):
        self.info = {}
        chain_type, chain_id = user_loc['domain'].split('://')
        self.address = ChainDNS.checkuser(chain_type, chain_id, user_loc['name'])
        self.chain_host = ChainDNS.gethost(chain_type, chain_id)
        self.name = user_loc['domain'] + '.' + user_loc['name']
        if 'passphrase' in user_loc:
            self.password = user_loc['passphrase']
        # for loc in user_loc:
        #     chain_type, chain_id = loc['chain'].split('://')
        #     if chain_type == 'Ethereum':
        #         self.address = ChainDNS.checkuser(chain_type, chain_id, loc['name'])
        #         self.chain_host = ChainDNS.gethost(chain_type, chain_id)
        #         if 'passphrase' in loc:
        #             self.password = loc['passphrase']
        #     self.info[chain_type] = {
        #         'address': ChainDNS.checkuser(chain_type, chain_id, loc['name']),
        #         'host': ChainDNS.gethost(chain_type, chain_id),
        #         'password': None
        #     }
        #     if 'passphrase' in loc:
        #         self.info[chain_type]['password'] = loc['passphrase']

    def unlockself(self):
        unlock = JsonRPC.personal_unlock_account(self.address, self.password, 20)
        response = JsonRPC.send(unlock, HTTP_HEADER, self.chain_host)
        if not response['result']:
            raise ValueError("unlock failed. wrong password?")

    def sign(self, msg):
        # assuming self.address is on Ethereum
        self.unlockself()
        sign_json = JsonRPC.eth_sign(self.address, msg)
        return JsonRPC.send(sign_json, HTTP_HEADER, self.chain_host)['result']

    @staticmethod
    def call(trans):
        if trans.chain_type == 'Ethereum':
            call_json = JsonRPC.eth_call(trans.jsonize())
            tx_response = JsonRPC.send(call_json, HTTP_HEADER, trans.chain_host)['result']
            # print(json.dumps(tx_response, sort_keys=True, indent=4, separators=(', ', ': ')))

            print(tx_response)

        else:
            raise TypeError("unsupported chain-type: ", + trans.chain_type)

    def send(self, trans, passphrase):
        if trans.chain_type == 'Ethereum':
            unlock = JsonRPC.personal_unlock_account(self.address, passphrase, 20)
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

    def ackinit(self, ves, isc, content, sig):
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

        # self.unlockself()
        # ack_func = isc.handle.user_ack(signatrue, {
        #     'from': Web3.toChecksumAddress(self.address),
        #     'gas': hex(5000000)
        # })
        # ack_func.transact()
        # print(ack_func.loop_and_wait())

        # not try but here ... TODO
        ret = ves.session_setup_update(int(content[0]), self.name, signatrue)
        if isinstance(ret, Exception):
            raise ret
        else:
            print("success")
