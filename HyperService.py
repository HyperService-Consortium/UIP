#!/usr/bin/python

import json, requests, time
from uiputils.ethtools import JsonRPC, AbiEncoder
from uiputils.uiptools.cast import uint64string
from uiputils.uiptypes.meta import StateProof, SmartContract

BLOCKCHAIN = {
    "A": "BuptChain1",
    "B": "Chain1",
    "C": "Rinkeby",
    "D": "Popsten"
}

NETWORK_SETUP = {
    # BLOCKCHAIN['A']: "http://162.105.87.118:8545",
    BLOCKCHAIN['B']: "http://127.0.0.1:8545",
    BLOCKCHAIN['C']: "http://127.0.0.1:8599",
    BLOCKCHAIN['D']: "http://127.0.0.1:8545"
}

# Configuration.
# "YourPassWord`"
UNLOCK_PWD = "123456"
HTTP_HEADERS = {'Content-Type': 'application/json'}
ACCOUNT_UNLOCK_PERIOD = 3000


class HyperService:
    def __init__(self, domains):
        self.domain_handles = {}
        self.EstablishBNVisibility(domains)
        self.contracts = {}

    def DispatchRpcToDomain(self, url, data):
        # dispatch RPC to domains(Blockchians)
        response = requests.post(
            url,
            headers=HTTP_HEADERS,
            data=json.dumps(data))
        if response.status_code != 200 or 'error' in response.json():
            print(json.dumps(data))
            raise Exception(response.json())

        return response.json()

    def EstablishBNVisibility(self, domains):
        for domain in domains:
            coinbase = JsonRPC.eth_coinbase()

            url = NETWORK_SETUP[domain]
            response = self.DispatchRpcToDomain(url, coinbase)
            self.domain_handles[domain] = response['result']

            # Unlock account for furture use.
            unlock = {
                    "jsonrpc": "2.0", 
                    "method": "personal_unlockAccount",
                    "params": [self.domain_handles[domain],
                        UNLOCK_PWD, ACCOUNT_UNLOCK_PERIOD],
                    "id": 64
                    }
            response = self.DispatchRpcToDomain(url, unlock)
            print(response)


    def DeployContract(self, contract):
        if contract.domain not in self.domain_handles:
            raise Exception("Unsupported domain: " + contract.domain)

        handle = self.domain_handles[contract.domain]

        transaction = {
                    "from": handle,
                    "data": contract.bytecode,
                    "gas": contract.gas,
                    "value": contract.value,
                    }

        deploy = JsonRPC.eth_send_transaction(transaction)

        url = NETWORK_SETUP[contract.domain]
        response = self.DispatchRpcToDomain(url, deploy)
        tx_hash = response['result']
        contract_addr = self.RetrieveContractAddress(url, tx_hash)
        print ("Contract is deployed at address: " + contract_addr)
        self.contracts[contract_addr] = contract

    def RetrieveContractAddress(self, url, tx_hash):
        get_tx = JsonRPC.eth_get_transaction_receipt(tx_hash)

        while True:
            response = self.DispatchRpcToDomain(url, get_tx)
            if response['result'] is None:
                print ("Contract is deploying, please stand by")
                time.sleep(2)
                continue

            block_number = response['result']['blockNumber']
            contract_addr = response['result']['contractAddress']
            get_code = JsonRPC.eth_get_code(contract_addr, block_number)

            code_resp = self.DispatchRpcToDomain(url, get_code)

            # print(code_resp)
            print(contract_addr)
            if code_resp['result'] == '0x':
                raise IndexError("Contract deployment failed")
            return contract_addr

    def GetAuthenticatedPriceFromBroker(self):
        for index, (addr, contract) in enumerate(self.contracts.items()):
            if contract.name is 'BrokerContract':
                return self.GetContractState(addr, 0)

    def GetContractState(self, contract, index, block="latest"):
        if contract not in self.contracts:
            raise Exception("No contract is found " + contract)
        
        domain = self.contracts[contract].domain
        url = NETWORK_SETUP[domain]
        get_state = JsonRPC.eth_get_storage_at(contract, hex(index), block)

        value_response = self.DispatchRpcToDomain(url, get_state)


        get_proof = JsonRPC.eth_get_proof(contract, [hex(index)], block)

        proof_response = self.DispatchRpcToDomain(url, get_proof)
        state_proof = proof_response['result']['storageProof']
        return StateProof(value_response['result'], block, state_proof)


def serializeNSBData(bytecode, addrlist, required):
    suffixdata = uint64string(40) + uint64string(required) + uint64string(len(addrlist))
    for x in addrlist:
        if x[0:2] == '0x':
            suffixdata += uint64string(x[2:])
        else:
            suffixdata += uint64string(x)
    return bytecode + suffixdata


if __name__ == '__main__':

    supported_chains = [BLOCKCHAIN['B']]  # [BLOCKCHAIN['A'],
    hyperservice = HyperService(supported_chains)

    # chain1 0x99d5c147122e79c30ce5e6ad793fc6716ced6f98
    # buptchain1 0xff10e1a886cfb4d1be8aa469c783e3492afc398d
    # with open('./contract/solidity/contract_sample/broker-option/broker.bin', 'r') as f:
    #     BrokerBytecode = f.read()
    #
    #     broker_contract = SmartContract(
    #         BrokerBytecode + AbiEncoder.encodes(
    #             [
    #                 ["0x7019fa779024c0a0eac1d8475733eefe10a49f3b"],
    #                 1
    #             ],
    #             ['address[]', 'uint']
    #         ),
    #         BLOCKCHAIN['B'],
    #         "BrokerContract", hex(2000000))
    #     hyperservice.DeployContract(broker_contract)
    #    # queryProof = hyperservice.GetAuthenticatedPriceFromBroker()
    #    # print(queryProof)

    # chain1 0x3723261b2a5a62b778b5c74318534d7fdf8db38c
    # buptchain1 0x1c8056438cb7b6b303b02520dbc30faeba805989
    # chain2 0xc06da79957ca0b46aac29ee2815742f05fbad327

    # with open('./contract/solidity/contract_sample/broker-option/option.bin', 'r') as f:
    #     OptionBytecode = f.read()
    #     option_contract = SmartContract(
    #         OptionBytecode + AbiEncoder.encodes(
    #             ["0xf4dacff5eba7426295e27a32d389fff3cde55de2", '10'],
    #             ['address', 'uint']
    #         ),
    #         BLOCKCHAIN['A'],
    #         "OptionContract", hex(1000000), "0x8772")
    #     hyperservice.DeployContract(option_contract)

    # chain1
    # 0x7019fa779024c0a0eac1d8475733eefe10a49f3b
    # buptchain1
    # 0x5bc26e3c0067c62b95ad11dfbfcbfc666876fdd4
    # 0x4f358c8e9b891082eb61fb96f1a0cbdf23c14b6b
    # with open('./contract/solidity/nsb/nsb.bin', 'r') as f:
    #     NSBBytecode = f.read()
    #     NSBdata = serializeNSBData(NSBBytecode, ["0x7019fa779024c0a0eac1d8475733eefe10a49f3b"], 1)
    #     NSB_contract = SmartContract(
    #         NSBdata, BLOCKCHAIN['B'],
    #         "NSBContract", hex(8000000))
    #     hyperservice.DeployContract(NSB_contract)

    # ethereum chain1
    # 0xa537235f11b50a89ba2b5007cdd5eb7fd3cb3f7e

    with open('./contract/hsapps/CryptoAsset/CryptoAsset.bin', 'r') as f:
        CryptoAssetBytecode = f.read()
        # NSBdata = serializeNSBData(NSBBytecode, ["0x7019fa779024c0a0eac1d8475733eefe10a49f3b"], 1)
        CryptoAssetContract = SmartContract(
            CryptoAssetBytecode, BLOCKCHAIN['B'],
            "CryptoAssetContract", hex(8000000))
        hyperservice.DeployContract(CryptoAssetContract)

    # print(hyperservice.contracts)
