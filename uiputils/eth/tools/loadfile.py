
# python modules
import json


class FileLoad(object):
    # simply load files
    def __int__(self):
        pass

    @staticmethod
    def getabi(contract_abi):
        if isinstance(contract_abi, str):
            with open(contract_abi, "r") as abi_file:
                return json.load(abi_file)
        else:
            return contract_abi

    @staticmethod
    def getbytecode(contract_bytecode):
        if isinstance(contract_bytecode, str):
            with open(contract_bytecode, "rb") as bytecode_file:
                return bytecode_file.read()
        else:
            return contract_bytecode

    @staticmethod
    def getopintents(op_intents):
        if isinstance(op_intents, str):
            with open(op_intents, "r") as intent_file:
                return json.load(intent_file)
        else:
            return op_intents
