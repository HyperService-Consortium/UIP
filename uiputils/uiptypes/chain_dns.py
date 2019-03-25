
# eth modules
from uiputils.eth.ethtypes import EthChainDNS


def adduser_f00(user):
    user_name, chain_domain = (split_str[::-1] for split_str in user[::-1].split('.', 1))
    chain_type, chain_id = chain_domain.split('://')
    return ChainDNS.checkuser(chain_type, chain_id, user_name)


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
