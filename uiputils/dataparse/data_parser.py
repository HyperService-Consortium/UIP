

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
                begining_pos, contract_addr, domain = [split_str[::-1] for split_str in arg[:0:-1].split('.', 2)]
                contract_addr, domain = eth_known_contract[contract_addr], ChainDNS.get_host(domain)
                authen_pos = HexBytes(SoliTypes[arg_type].loc(begining_pos)).hex()
                parsed_args.append(JsonRPC.send(
                    JsonRPC.eth_get_storage_at(contract_addr, authen_pos, "latest"),
                    HTTP_HEADER,
                    domain
                )['result'])
            else:
                parsed_args.append(arg)
        return AbiEncoder.encodes(parsed_args, args_types)
