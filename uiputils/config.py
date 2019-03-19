
import os.path as parsepath

INCLUDE_PATH = parsepath.dirname(__file__) + "/include"

HTTP_HEADER = {'Content-Type': 'application/json'}

ETHSIGN_HEADER = b"\x19Ethereum Signed Message:\n"

eth_blockchain_info = {
    'chain1': {
        'host': 'http://127.0.0.1:8545',
        'relay': "0x7019fa779024c0a0eac1d8475733eefe10a49f3b",
        'user': {
            'X': "0x47a1cdb6594d6efed3a6b917f2fbaa2bbcf61a2e"
        }
    },
    'chain2': {
        'host': 'http://127.0.0.1:8545',
        'relay': "0xd051a43d3ea62afff3632bca3d5abf68bc6fd737",
        'user': {
            'Y': "0x91f030cfec606f9ff832aef20f768bf3a129b59c"
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
