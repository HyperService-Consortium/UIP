
'some cast method'

__author__ = 'Myriad Dreamin'

import json


class FileLoad(object):
    # simply load files
    def __int__(self):
        pass

    @staticmethod
    def getabi(contract_abi):
        if isinstance(contract_abi, str):
            with open(contract_abi, "r") as abifile:
                return json.load(abifile)
        else:
            return contract_abi

    @staticmethod
    def getbytecode(contract_bytecode):
        if isinstance(contract_bytecode, str):
            with open(contract_bytecode, "rb") as bytecodefile:
                return bytecodefile.read()
        else:
            return contract_bytecode