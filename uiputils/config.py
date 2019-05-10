
import os.path as parsepath
import logging.handlers


INCLUDE_PATH = parsepath.dirname(__file__) + "/include"
ROOT_PATH = parsepath.dirname(parsepath.dirname(__file__))

HTTP_HEADER = {'Content-Type': 'application/json'}

ETHSIGN_HEADER = b"\x19Ethereum Signed Message:\n"

eth_blockchain_info = {
    'chain1': {
        'host': 'http://127.0.0.1:8545',
        'user': {
            'X': "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e",
            'a2': "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e",
            "a1": "0xd051a43d3ea62afff3632bca3d5abf68bc6fd737",
            'nsb': "0x4f984aa7d262372df92f85af9be8d2df09ac4018",
            'relay_nsb': "0x7019fa779024c0a0eac1d8475733eefe10a49f3b"
        }
    },
    'chain2': {
        'host': 'http://127.0.0.1:8545',
        'user': {
            'Y': "0x91f030cfec606f9ff832aef20f768bf3a129b59c",
            'relay_nsb': "0xd051a43d3ea62afff3632bca3d5abf68bc6fd737"
        }
    },
    "BuptChain1": {
        'host': 'http://162.105.87.118:8545',
        'user': {
            "a2": "0xf4dacff5eba7426295e27a32d389fff3cde55de2"
        }
    }
}

tennsb_blockchain_info = {
    'chain1': {
        'host': "http://47.254.66.11:26657",
        'user': {
            "a2": "0xcfe900c7a56f87882f0e18e26851bce7b7e61ebeca6c4b235fa360d627dfac63",
            "relay_nsb": "0xcfe900c7a56f87882f0e18e26851bce7b7e61ebeca6c4b235fa360d627dfac63"
        }
    }
}


eth_unit_factor = {
    'iew':    0.5,
    'wei':    1,
    'kwei':   1000,
    'mwei':   1000000,
    'gwei':   1000000000,
    'szabo':  1000000000000,
    'finney': 1000000000000000,
    'ether':  1000000000000000000
}

tennsb_unit_factor = {
    'iew':    1,
    'wei':    2,
    'kwei':   2000,
    'mwei':   2000000,
    'gwei':   2000000000,
    'szabo':  2000000000000,
    'finney': 2000000000000000,
    'ether':  2000000000000000000
}

trans_factor = {
    'Ethereum': {
        'Tendermint': 2,
    },
    'Tendermint': {
        'Ethereum': 0.5,
    }
}


eth_default_gasuse = hex(300000)

eth_known_contract = {
    'c1': {
        "address": "0x7c7b26fa65e091f7b9f23db77ad5f714f1dae5ea",
        "host": "http://127.0.0.1:8545"
    },
    'c2': {
        "address": "0xbc03fb164c168b9364e820395fbf6ebdbc8f7ffe",
        "host": "http://162.105.87.118:8545"
    }
}

ves_log_dir = ROOT_PATH + "/log/ves.log"

isc_log_dir = ROOT_PATH + "/log/isc.log"

isc_abi_dir = INCLUDE_PATH + "/isc.abi"

isc_bin_dir = INCLUDE_PATH + "/isc.bin"
