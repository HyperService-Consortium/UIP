
'some cast methods'


def uintxstring(num, x):
    nums = str(num)
    return "0" * (x - len(nums)) + nums


def uint32string(num):
    nums = str(num)
    return "0" * (32 - len(nums)) + nums


def uint64string(num):
    nums = str(num)
    return "0" * (64 - len(nums)) + nums


def uint128string(num):
    nums = str(num)
    return "0" * (128 - len(nums)) + nums


def uint256string(num):
    nums = str(num)
    return "0" * (256 - len(nums)) + nums

