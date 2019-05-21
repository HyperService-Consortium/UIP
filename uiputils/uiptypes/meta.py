

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


class StateProof:
    # The Merkle Proof for a Blockchain state.
    def __init__(self, value, block, proof):
        self.value = value
        self.block = block
        self.proof = proof

    def __str__(self):
        return "value: %s;block: %s;proof: %s;" % (self.value, self.block, self.proof)
