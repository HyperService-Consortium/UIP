
import os.path as parsepath

INCLUDE_PATH = parsepath.dirname(__file__) + "/include"
ROOT_PATH = parsepath.dirname(parsepath.dirname(__file__))

HTTP_HEADER = {'Content-Type': 'application/json'}

ETHSIGN_HEADER = b"\x19Ethereum Signed Message:\n"

eth_blockchain_info = {
    'chain1': {
        'host': 'http://127.0.0.1:8545',
        'user': {
            'X': "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e",
            "a1": "0x7019fa779024c0a0eac1d8475733eefe10a49f3b",
            'nsb': "0x4f984aa7d262372df92f85af9be8d2df09ac4018",
            'relay_nsb': "0x7019fa779024c0a0eac1d8475733eefe10a49f3b"
        }
    },
    'Chain1': {
        'host': 'http://127.0.0.1:8545',
        'user': {
            'X': "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e",
            'a2': "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e",
            "a1": "0x7019fa779024c0a0eac1d8475733eefe10a49f3b",
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

eth_unit_factor = {
    'wei':    1,
    'kwei':   1000,
    'mwei':   1000000,
    'gwei':   1000000000,
    'szabo':  1000000000000,
    'finney': 1000000000000000,
    'ether':  1000000000000000000
}

eth_default_gasuse = hex(300000)

ves_log_dir = ROOT_PATH + "/log/ves.log"

isc_log_dir = ROOT_PATH + "/log/isc.log"
