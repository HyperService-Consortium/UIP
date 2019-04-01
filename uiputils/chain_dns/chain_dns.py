
# python modules


# ethereum modules
from eth_utils import is_address


# uip modules
from uiputils.errors import Missing


# config
from uiputils.config import eth_blockchain_info


def adduser_f00(user):
    user_name, chain_domain = (split_str[::-1] for split_str in user[::-1].split('.', 1))
    chain_type, chain_id = chain_domain.split('://')
    return ChainDNS.checkuser(chain_type, chain_id, user_name)


class EthChainDNS:
    def __init__(self):
        pass

    @staticmethod
    def checkuser(chain_id, user_name):
        if is_address(user_name):
            return user_name
        if chain_id in eth_blockchain_info:
            if user_name in eth_blockchain_info[chain_id]['user']:
                return eth_blockchain_info[chain_id]['user'][user_name]
            raise Missing('no user named ' + user_name + ' in ' + chain_id)
        else:
            raise Missing('no such chainID: ' + chain_id)

    @staticmethod
    def checkrelay(chain_id):
        if chain_id in eth_blockchain_info:
            if 'relay' in eth_blockchain_info[chain_id]:
                return eth_blockchain_info[chain_id]['relay']
            else:
                raise Missing('this chain has not relay-address' + chain_id)
        else:
            raise Missing('no such chainID: ' + chain_id)

    @staticmethod
    def gethost(chain_id):
        if chain_id in eth_blockchain_info:
            return eth_blockchain_info[chain_id]['host']
        else:
            raise Missing('no such chainID: ' + chain_id)


class ChainDNS:
    DNSmethod = {
       'Ethereum': EthChainDNS
    }
    adduser = {
        'dot-concated': adduser_f00
    }

    @staticmethod
    def checkuser(chain_type, chain_id, user_name):
        # this function doesn't check chain_type
        return ChainDNS.DNSmethod[chain_type].checkuser(chain_id, user_name)

    @staticmethod
    def checkrelay(chain_type, chain_id):
        # this function doesn't check chain_type
        return ChainDNS.DNSmethod[chain_type].checkrelay(chain_id)

    @staticmethod
    def gethost(chain_type, chain_id):
        return ChainDNS.DNSmethod[chain_type].gethost(chain_id)

    @staticmethod
    def gatherusers(users, userformat=None):
        if userformat is None:
            # TODO: multi-format of ChainDNS.gatherusers
            pass
        users_address = []
        if userformat == 'dot-concated':
            for formated_user in users:
                users_address.append(ChainDNS.adduser['dot-concated'](formated_user))
        else:
            raise KeyError(userformat + ' unsupported now')
        return users_address
