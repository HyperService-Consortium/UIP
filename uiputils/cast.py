
'some cast methods'


def uintxstring(num, x):
	# return x-bit string of num
    nums = str(num)
    return "0" * (x - len(nums)) + nums


def uint32string(num):
	# return 32-bit string of num
    nums = str(num)
    return "0" * (32 - len(nums)) + nums


def uint64string(num):
	# return 64-bit string of num
    nums = str(num)
    return "0" * (64 - len(nums)) + nums


def uint128string(num):
	# return 128-bit string of num
    nums = str(num)
    return "0" * (128 - len(nums)) + nums


def uint256string(num):
	# return 256-bit string of num
    nums = str(num)
    return "0" * (256 - len(nums)) + nums

def uintxhexstring(num, x):
	# return x-bit string of num
    nums = str(hex(num))
    return "0" * (x - len(nums)) + nums


def uint32hexstring(num):
	# return 32-bit string of num
    nums = str(hex(num))[2:]
    return "0" * (32 - len(nums)) + nums


def uint64hexstring(num):
	# return 64-bit string of num
    nums = str(hex(num))[2:]
    return "0" * (64 - len(nums)) + nums


def uint128hexstring(num):
	# return 128-bit string of num
    nums = str(hex(num))[2:]
    return "0" * (128 - len(nums)) + nums


def uint256hexstring(num):
	# return 256-bit string of num
    nums = str(hex(num))[2:]
    return "0" * (256 - len(nums)) + nums


if __name__ == '__main__':
    print(uintxstring(15, 8))
    print(uint32string(15))
    print(uint64string(15))
    print(uint128string(15))
    print(uintxhexstring(15, 8))
    print(uint32hexstring(15))
    print(uint64hexstring(15))
    print(uint128hexstring(15))
    print(uint64hexstring(int('0x0', 16)))
