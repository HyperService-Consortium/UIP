
# python modules
import re

# patterns
#   match the hex without prefix "0x"
hex_match = re.compile(r'\b[0-9a-fA-F]+\b')
#   match the hex with prefix "0x"
hex_match_withprefix = re.compile(r'\b0x[0-9a-fA-F]+\b')
