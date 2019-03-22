
# ethereum modules
from web3 import Web3


class ServiceStart(object):
    # simply start services
    def __int__(self):
        pass

    @staticmethod
    def startweb3(host):
        if isinstance(host, str):
            return Web3(Web3.HTTPProvider(host, request_kwargs={'timeout': 10}))
        else:
            return host
