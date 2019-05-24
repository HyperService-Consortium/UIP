
import base64
import json

from py_nsbcli.types import TransactionHeader
from py_nsbcli.modules.contract import Contract
from py_nsbcli.util.cast import transbytes
from py_nsbcli.util import GoJson


class DelegateContract(Contract):
    def __init__(self, bind_cli):
        super().__init__(bind_cli)

    def create_delegate(self, wlt, owners, district, total_votes):
        args_delegate = {
            "1": owners,
            "2": district,
            "3": transbytes(total_votes, 32)
        }

        tx_header = TransactionHeader(wlt.address(0), None, GoJson.dumps(args_delegate).encode())
        tx_header.sign(wlt)
        return self.create_contract("delegate", tx_header)

    def vote(self, wlt, contract_address=None):
        data = {
            "function_name": "Vote",
            "args": ""
        }
        # This is printed when contract is deployed.
        if contract_address is None:
            contract_address = self.address
        else:
            if isinstance(contract_address, str):
                if contract_address[0:2] == "0x":
                    contract_address = contract_address[2:]
                contract_address = bytes.fromhex(contract_address)
        tx_header = TransactionHeader(wlt.address(0), contract_address, json.dumps(data).encode())
        tx_header.sign(wlt)
        return self.exec_contract_method("delegate", tx_header)
