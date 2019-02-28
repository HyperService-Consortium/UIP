#!/usr/bin/python

import json, requests, time
from uiputils.jsonrpc import JsonRPC
import uiputils.cast as converter

BLOCKCHAIN_A = "private_A"
BLOCKCHAIN_B = "private_B"
BLOCKCHAIN_C = "Rinkeby"
BLOCKCHAIN_D = "Popsten"

NETWORK_SETUP = {
        BLOCKCHAIN_A: "http://127.0.0.1:8545",
        BLOCKCHAIN_B: "http://127.0.0.1:8599",
        BLOCKCHAIN_C: "http://127.0.0.1:8545",
        BLOCKCHAIN_D: "http://127.0.0.1:8545"
        }

# Configuration.
# "YourPassWord`"
UNLOCK_PWD = "123456"
HTTP_HEADERS = {'Content-Type': 'application/json'}
ACCOUNT_UNLOCK_PERIOD = 3000
ETHDB_PATH = "D:\\Go Ethereum\\data\\geth\\chaindata"


class BlockchainNetwork:
    def __init__(self, identifer="", rpc_port=0, data_dir="", listen_port=0, host="", public=False):
        self.identifer = identifer
        self.rpc_port = rpc_port
        self.data_dir = data_dir
        self.listen_port = listen_port
        self.host = host
        self.public = public


class SmartContract:
    # The abstracted structure of a SmartContract.
    def __init__(self, bytecode="", domain="", name="", gas=hex(0), value=hex(0)):
        self.bytecode = bytecode
        self.domain = domain
        self.name = name
        self.gas = gas
        self.value = value


# The Merkle Proof for a Blockchain state.
class StateProof:
    def __init__(self, value, block, proof):
        self.value = value
        self.block = block
        self.proof = proof

    def __str__(self):
        return "value: %s;block: %s;proof: %s;" % (self.value, self.block, self.proof);


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
    suffixdata = converter.uint64string(40) + converter.uint64string(required) + converter.uint64string(len(addrlist))
    for x in addrlist:
        if x[0:2] == '0x':
            suffixdata += converter.uint64string(x[2:])
        else:
            suffixdata += converter.uint64string(x)
    return bytecode + suffixdata


if __name__ == '__main__':

    supported_chains = [BLOCKCHAIN_A]#, BLOCKCHAIN_B]
    hyperservice = HyperService(supported_chains)

    # Deploy the Broker and Option contract.
    # with open('broker_bytecode', 'r') as f:
    #     BrokerBytecode = f.read()
    #     print(BrokerBytecode[:-1])
    #     broker_contract = SmartContract(
    #         BrokerBytecode[:-1], BLOCKCHAIN_A,
    #         "BrokerContract", hex(2000000))
    #     hyperservice.DeployContract(broker_contract)
    #     queryProof = hyperservice.GetAuthenticatedPriceFromBroker()
    #     print(queryProof)

    # with open('option_bytecode', 'r') as f:
    #     OptionBytecode = f.read()
    #     option_contract = SmartContract(
    #         OptionBytecode[:-1], BLOCKCHAIN_A,
    #         "OptionContract", hex(200000), "0x8ac7230489e80000")
    #     hyperservice.DeployContract(option_contract)

    with open('./nsb/nsb.bin', 'r') as f:
        NSBBytecode = f.read()
        # print(NSBBytecode[:])
        bycde = serializeNSBData(NSBBytecode, ["0xe1300d8ea0909faa764c316436ad0ece571f62b2"], 1)
        print(bycde)
        NSB_contract = SmartContract(
            bycde, BLOCKCHAIN_A,
            "NSBContract", hex(10000000))
        hyperservice.DeployContract(NSB_contract)

    # print(hyperservice.contracts)
