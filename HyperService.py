#!/usr/bin/python

import json, requests, time
from uiputils.eth import JsonRPC
from uiputils.cast import uint64string
from uiputils.uiptypes import StateProof, SmartContract

BLOCKCHAIN = {
    "A": "private_A",
    "B": "private_B",
    "C": "Rinkeby",
    "D": "Popsten"
}

NETWORK_SETUP = {
    BLOCKCHAIN['A']: "http://127.0.0.1:8545",
    BLOCKCHAIN['B']: "http://127.0.0.1:8599",
    BLOCKCHAIN['C']: "http://127.0.0.1:8545",
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
            coinbase = JsonRPC.ethCoinbase()

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

        deploy = JsonRPC.ethSendTransaction(transaction)

        url = NETWORK_SETUP[contract.domain]
        response = self.DispatchRpcToDomain(url, deploy)
        tx_hash = response['result']
        contract_addr = self.RetrieveContractAddress(url, tx_hash)
        print ("Contract is deployed at address: " + contract_addr)
        self.contracts[contract_addr] = contract

    def RetrieveContractAddress(self, url, tx_hash):
        get_tx = JsonRPC.ethGetTransactionReceipt(tx_hash)

        while True:
            response = self.DispatchRpcToDomain(url, get_tx)
            if response['result'] is None:
                print ("Contract is deploying, please stand by")
                time.sleep(2)
                continue

            block_number = response['result']['blockNumber']
            contract_addr = response['result']['contractAddress']
            get_code = JsonRPC.ethGetCode(contract_addr, block_number)

            code_resp = self.DispatchRpcToDomain(url, get_code)

            # print(code_resp)
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
        get_state = JsonRPC.ethGetStorageAt(contract, hex(index), block)

        value_response = self.DispatchRpcToDomain(url, get_state)


        get_proof = JsonRPC.ethGetProof(contract, [hex(index)], block)

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

    supported_chains = [BLOCKCHAIN['A']]#, BLOCKCHAIN['A']]
    hyperservice = HyperService(supported_chains)

    # Deploy the Broker and Option contract.
    # with open('broker_bytecode', 'r') as f:
    #     BrokerBytecode = f.read()
    #     print(BrokerBytecode[:-1])
    #     broker_contract = SmartContract(
    #         BrokerBytecode[:-1], BLOCKCHAIN['A'],
    #         "BrokerContract", hex(2000000))
    #     hyperservice.DeployContract(broker_contract)
    #     queryProof = hyperservice.GetAuthenticatedPriceFromBroker()
    #     print(queryProof)

    # with open('option_bytecode', 'r') as f:
    #     OptionBytecode = f.read()
    #     option_contract = SmartContract(
    #         OptionBytecode[:-1], BLOCKCHAIN['A'],
    #         "OptionContract", hex(200000), "0x8ac7230489e80000")
    #     hyperservice.DeployContract(option_contract)

    # 0x7019fa779024c0a0eac1d8475733eefe10a49f3b
    with open('./nsb/nsb.bin', 'r') as f:
        NSBBytecode = f.read()
        NSBdata = serializeNSBData(NSBBytecode, ["0x7019fa779024c0a0eac1d8475733eefe10a49f3b"], 1)
        NSB_contract = SmartContract(
            NSBdata, BLOCKCHAIN['A'],
            "NSBContract", hex(10000000))
        hyperservice.DeployContract(NSB_contract)

    # print(hyperservice.contracts)
