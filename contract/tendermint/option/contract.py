

import base64
import json

from py_nsbcli.types import TransactionHeader
from py_nsbcli.modules.contract import Contract
from py_nsbcli.util.cast import transbytes


class Option(Contract):
    def __init__(self, bind_cli):
        super().__init__(bind_cli)

    def create_option(self, wlt, owner, price, value):
        value = transbytes(price, 32)
        args_option = {
            "owner": base64.b64encode(owner).decode(),
            "strike_price": base64.b64encode(value).decode()
        }
        tx_header = TransactionHeader(wlt.address(0), None, json.dumps(args_option).encode(), value)
        tx_header.sign(wlt)
        return self.create_contract("option", tx_header)

    def update_stake(self, wlt, price, contract_address=None):
        price = transbytes(price, 32)
        data = {
            "function_name": "UpdateStake",
            "args": base64.b64encode(json.dumps({
                "1": base64.b64encode(transbytes(price, 32)).decode()
            }).encode()).decode()
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
        return self.exec_contract_method("option", tx_header)

    def buy_option(self, wlt, price, contract_address=None):
        price = transbytes(price, 32)
        data = {
            "function_name": "BuyOption",
            "args": base64.b64encode(json.dumps({
                "1": base64.b64encode(transbytes(price, 32)).decode()
            }).encode()).decode()
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
        return self.exec_contract_method("option", tx_header)
