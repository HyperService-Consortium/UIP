
# python modules
import re

# patterns
#   match the hex without prefix "0x"
hex_match = re.compile(r'\b[0-9a-fA-F]+\b')
#   match the hex with prefix "0x"
hex_match_withprefix = re.compile(r'\b0x[0-9a-fA-F]+\b')


def is_address(addr) -> bool:
    if isinstance(addr, str):
        if hex_match_withprefix.match(addr):
            return len(addr) == 66
        if hex_match.match(addr):
            return len(addr) == 64
        return False
    elif isinstance(addr, bytes):
        return len(addr) == 32
    else:
        return False

