

import enum
import os.path as parsepath
import logging.handlers
import platform

from py_nsbcli import KVDB, LevelDB


class AttestationType(enum.Enum):
    using_secp256k1 = 0
    using_eddsa25519 = 1


INCLUDE_PATH = parsepath.dirname(__file__) + "/include"
ROOT_PATH = parsepath.dirname(parsepath.dirname(__file__))

HTTP_HEADER = {'Content-Type': 'application/json'}

ETHSIGN_HEADER = b"\x19Ethereum Signed Message:\n"


action_using_flag = {
    'Ethereum': AttestationType.using_secp256k1,
    'Tendermint': AttestationType.using_eddsa25519
}


eth_blockchain_info = {
    'legacy_chain1': {
        'host': 'http://127.0.0.1:8545',
        'user': {
            'X': "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e",
            'a2': "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e",
            "a1": "0xd051a43d3ea62afff3632bca3d5abf68bc6fd737",
            'nsb': "0x4f984aa7d262372df92f85af9be8d2df09ac4018",
            'relay_nsb': "0x7019fa779024c0a0eac1d8475733eefe10a49f3b"
        }
    },
    'chain1': {
        'host': 'http://127.0.0.1:8545',
        'user': {
            'X': "0x981739a13593980763de3353340617ef16da6354",
            'a2': "0x981739a13593980763de3353340617ef16da6354",
            "a1": "0x93334ae4b2d42ebba8cc7c797bfeb02bfb3349d6",
            'relay_nsb': "0x0ac45f1e6b8d47ac4c73aee62c52794b5898da9f"
        }
    },
    'chain2': {
        'host': 'http://127.0.0.1:8545',
        'user': {
            'Y': "0x91f030cfec606f9ff832aef20f768bf3a129b59c",
            'relay_nsb': "0xd051a43d3ea62afff3632bca3d5abf68bc6fd737"
        }
    },
    "chain3": {
        'host': 'http://162.105.87.118:8545',
        'user': {
            "a1": "0x09e47d885f6e79e47257a49499301a917e2154f2",
            "a2": "0xf4dacff5eba7426295e27a32d389fff3cde55de2",
            "relay_nsb": "0x35a9c4e9aee7695e3dcf3bc2c753abaa9c1c3d71"
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
        'host': "http://47.251.2.73:26657",  # "http://47.254.66.11:26657",
        'user': {
            "a1": "0x604bdd2dd4b7e1b761e2ac96db99bb2bda386bb0d075b51a8f49c5103ebaa985",
            "a2": "0xcfe900c7a56f87882f0e18e26851bce7b7e61ebeca6c4b235fa360d627dfac63",
            "a3": "0x4f7a1b3d9f2f8f3e2c7e7729bc873fc55e607e47309941391a7a82673e563887",
            "relay_nsb": "0xcfe900c7a56f87882f0e18e26851bce7b7e61ebeca6c4b235fa360d627dfac63"
        }
    },
    'chain2': {
        'host': "http://47.251.2.73:26657",
        'user': {
            "a1": "0x604bdd2dd4b7e1b761e2ac96db99bb2bda386bb0d075b51a8f49c5103ebaa985",
            "a2": "0x4f7a1b3d9f2f8f3e2c7e7729bc873fc55e607e47309941391a7a82673e563887",
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
        "host": "http://162.105.87.118:8545"
    },
    'c2': {
        "address": "0xbc03fb164c168b9364e820395fbf6ebdbc8f7ffe",
        "host": "http://162.105.87.118:8545"
    }
}

tendermint_known_contract = {
    'c1': {
        "address": "0x7c7b26fa65e091f7b9f23db77ad5f714f1dae5ea",
        "host": "http://47.251.2.73:26657"
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

if platform.system() == "Windows":
    kvdb_path = "E:/project/go/src/github.com/Myriad-Dreamin/NSB/bin/kvstore"
else:
    kvdb_path = "/Users/zhuotaoliu/Development/HyperService//NSB/bin/kvstore"

kvdb = KVDB(LevelDB(kvdb_path))

alice = kvdb.load_wallet("Alice")
bob = kvdb.load_wallet("Bob")
tom = kvdb.load_wallet("Tom")
