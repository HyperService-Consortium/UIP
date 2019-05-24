

from hexbytes import HexBytes

from uiputils.ethtools import JsonRPC, AbiEncoder, SoliTypes
from uiputils.config import eth_known_contract
from uiputils.chain_dns import ChainDNS
from uiputils.config import HTTP_HEADER


class EthDataParser:

    @staticmethod
    def parse(args, args_types):
        parsed_args = []
        for arg, arg_type in zip(args, args_types):
            if isinstance(arg, str) and len(arg) > 0 and arg[0] == '@':
                try:
                    contract_addr, begining_pos = arg[1:].split('.')
                    contract_addr, domain = \
                        eth_known_contract[contract_addr]['address'], eth_known_contract[contract_addr]['host']
                    authen_pos = HexBytes(SoliTypes[arg_type].ori_loc(begining_pos)).hex()
                    # print(authen_pos, contract_addr, domain)
                    parsed_args.append(JsonRPC.send(
                        JsonRPC.eth_get_storage_at(contract_addr, authen_pos, "latest"),
                        HTTP_HEADER,
                        domain
                    )['result'])
                except:
                    parsed_args.append("012")
            else:
                parsed_args.append(arg)
        return AbiEncoder.encodes(parsed_args, args_types)
