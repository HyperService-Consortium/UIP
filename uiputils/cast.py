
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


if __name__ == '__main__':
    print(uintxstring(15, 8))
    print(uint32string(15))
    print(uint64string(15))
    print(uint128string(15))
