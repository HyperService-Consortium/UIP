
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


if __name__ == '__main__':
    print(uintxstring(15, 8))
    print(uint32string(15))
    print(uint64string(15))
    print(uint128string(15))
