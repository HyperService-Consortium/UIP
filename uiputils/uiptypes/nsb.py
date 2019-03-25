from uiputils.eth.ethtypes import EthNetStatusBlockchain as ethNSB


class NetworkStatusBlockChain:
    def __init__(self, nsb_type="ethereum", *args, **kwargs):
        if nsb_type == "ethereum":
            self.handle = ethNSB(*args, **kwargs)
        else:
            self.handle = None
            raise TypeError("other NSB type not implemented")
