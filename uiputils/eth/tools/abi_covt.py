
# eth modules
from uiputils.uiperror import Mismatch, SolidityTypeError

# ethereum modules
from hexbytes import HexBytes

# __init__ provided parterns
from .patterns import hex_match, hex_match_withprefix

# constant
#   X & MOD6 == X % 64
MOD6 = (1 << 6) - 1
#   INTM[c] - X == ~X (mod 2^{8c})
INTM = [(1 << (bit_size << 3)) for bit_size in range(33)]
#   two nibbles(0~15) represent a bytes(0~256)
BYTE32_LENGTH = 64
# encode
ENC = 'utf-8'

class AbiEncoder:
    def __init__(self):
        pass

    @staticmethod
    def encode(para_type, para):
        if para_type == 'address':
            return AbiEncoder.encode('uint160', para)
        elif para_type == 'string':
            return AbiEncoder.encode('bytes', para.encode('utf-8'))
        elif para_type == 'byte':
            return AbiEncoder.encode('bytes1', para)
        elif para_type == 'bool':
            return AbiEncoder.encode('uint8', para)
        elif para_type[-1] == ']':  # Array
            if not hasattr(para, '__iter__'):
                raise TypeError("not iteraable parameter " + str(para) + " for Array type " + para_type)
            array_type, array_size = para_type[:-1].split('[')
            if array_size != "":
                if int(array_size) < len(para):  # != ?
                    raise Mismatch('parameters mismatch with parameters_type')
                return ''.join((AbiEncoder.encode(array_type, ele) for ele in para))
            else:  # bug __iter__ -> __len__ ?
                return AbiEncoder.encode('uint256', len(para)) + \
                       ''.join((AbiEncoder.encode(array_type, ele) for ele in para))
        elif para_type[0:3] == 'int':
            numstr, negative_flag = para, '0'
            numsize = para_type[3:]
            if numsize == "":
                numsize = 32
            else:
                numsize = int(numsize)
                if (numsize & 7) != 0 or numsize > 256 or numsize < 0:
                    raise SolidityTypeError("invalid given-datatype: " + para_type)
                numsize >>= 2
            if isinstance(para, str):
                if not hex_match.match(para) and not hex_match_withprefix.match(para):
                    raise TypeError("invalid hexstring" + para + " for initializing datatype " + para_type)
            elif isinstance(para, int):
                if para < 0:
                    negative_flag = 'f'
                    numstr = hex(INTM[numsize >> 1] + para)[2:]
                else:
                    numstr = hex(numstr)[2:]
            else:
                raise TypeError("unexpected type " + type(para) + " for initializing datatype " + para_type)
            if len(numstr) > numsize:
                raise OverflowError("too large number " + str(para) + " to fill in type" + para_type)
            return negative_flag * (BYTE32_LENGTH - len(numstr)) + numstr
        elif para_type[0:4] == 'uint':
            if isinstance(para, str):
                if not hex_match.match(para) and not hex_match_withprefix.match(para):
                    raise TypeError("invalid hexstring " + para + " for initializing datatype " + para_type)
                if para[1] == 'x':
                    numstr = para[2:]
                else:
                    numstr = para
            elif isinstance(para, int):
                if para < 0:
                    raise ValueError("negative number " + str(para) + " for initializing datatype " + para_type)
                numstr = hex(para)[2:]
            else:
                raise TypeError("unexpected type " + str(type(para)) + " for initializing datatype " + para_type)
            numsize = para_type[4:]
            if numsize == "":
                numsize = 64
            else:
                numsize = int(numsize)
                if (numsize & 7) != 0 or numsize > 256 or numsize < 0:
                    raise SolidityTypeError("invalid datatype: " + para_type)
                numsize >>= 2
            if len(numstr) > numsize:
                raise OverflowError("too large number " + str(para) + " to fill in type " + para_type)
            return '0' * (BYTE32_LENGTH - len(numstr)) + numstr
        elif para_type[0:5] == 'bytes':
            if isinstance(para, bytes):
                para = HexBytes(para).hex()[2:]
            elif isinstance(para, str):
                if not hex_match.match(para) and not hex_match_withprefix.match(para):
                    para = bytes(para.encode(ENC))
                if para[1] == 'x':
                    para = para[2:]
            bytes_size = para_type[5:]
            if bytes_size == "":
                # print(para)
                if len(para) & 1:
                    raise Mismatch("odd-length byte-array is invalid")
                return AbiEncoder.encode('uint256', len(para) >> 1) + para + '0' * ((-len(para)) & MOD6)
            else:
                bytes_size = int(bytes_size)
                if len(para) != (bytes_size << 1):
                    raise Mismatch("parameter " + para + " doesn't match the datatype " + para_type)
                if bytes_size > 32:
                    raise SolidityTypeError("invalid given-datatype " + para_type)
                return para + '0' * ((-len(para)) & MOD6)
        raise SolidityTypeError("unexpected or invalid given-datatype: " + para_type)

    @staticmethod
    def is_array_type(para_type):
        return para_type[-1] == ']' or para_type == 'bytes' or para_type == 'string'

    @staticmethod
    def encodes(para_list, para_type_list):
        if len(para_list) != len(para_type_list):
            raise Mismatch('parameters mismatch with parameters_type_list')
        args_count, args_head, args_arrays = (len(para_type_list) << 5), "", ""

        for para_type, para in zip(para_type_list, para_list):
            ret = AbiEncoder.encode(para_type, para)
            if AbiEncoder.is_array_type(para_type):
                args_head += AbiEncoder.encode('uint256', args_count)
                args_arrays += ret
                args_count += (len(ret) >> 1)
            else:
                args_head += ret
        return args_head + args_arrays


class AbiDecoder:
    def __init__(self):
        pass

    @staticmethod
    def decode(ret_type, raw_ret):
        if ret_type == 'address':
            return AbiDecoder.decode('uint160', raw_ret)
        elif ret_type == 'byte':
            return AbiDecoder.decode('bytes1', raw_ret)
        elif ret_type == 'bool':
            return AbiDecoder.decode('uint8', raw_ret) != 0
        elif ret_type[-1] == ']':  # Array
            array_type, array_size = ret_type[:-1].split('[')
            if array_size != "":
                print("TODO array-type:", ret_type)
                pass
            else:
                raise SolidityTypeError("unsupported atom-solidity type" + ret_type)
        elif ret_type[0:3] == 'int':
            if raw_ret[0] == 'f':
                return int(raw_ret, 16) - INTM[32]
            return int(raw_ret, 16)
        elif ret_type[0:4] == 'uint':
            return int(raw_ret, 16)
        elif ret_type[0:5] == 'bytes':
            bytes_size = int(ret_type[5:])
            if bytes_size == "":
                raise SolidityTypeError("unsupported atom-solidity type: bytes")
            return HexBytes(raw_ret[0:(bytes_size << 1)])
        elif ret_type == 'string':
            raise SolidityTypeError("unsupported atom-solidity type: string")

        raise SolidityTypeError("unexpected or invalid given-datatype: " + ret_type)

    @staticmethod
    def is_array_type(para_type):
        return para_type[-1] == ']' or para_type == 'bytes' or para_type == 'string'

    @staticmethod
    def decode_array(ret_type, raw_rets):
        if 64 > len(raw_rets):
            raise OverflowError("superflours decode for array: input " + str(len(raw_rets)) + " but expect at least 64")
        if ret_type == 'bytes':
            ret_size = AbiDecoder.decode('uint256', raw_rets[0:64])
            if 64 + (ret_size << 1) > len(raw_rets):
                raise OverflowError(
                    "superflours decode for array: input " + str(len(raw_rets)) + \
                    " but expect at least " + str(64 + (ret_size << 1))
                )
            return HexBytes(raw_rets[64:64 + (ret_size << 1)])
        elif ret_type == 'string':
            ret_size = AbiDecoder.decode('uint256', raw_rets[0:64])
            if 64 + (ret_size << 1) > len(raw_rets):
                raise OverflowError(
                    "superflours decode for array: input " + str(len(raw_rets)) + \
                    " but expect at least " + str(64 + (ret_size << 1))
                )
            return raw_rets[64:64 + (ret_size << 1)].encode('utf-8')
        else:
            if ret_type[-2:] == '[]':
                if ret_type[-3] == ']':
                    print("TODO array-type:", ret_type)
                    return
                ret_size = AbiDecoder.decode('uint256', raw_rets[0:64])
                if 64 + (ret_size << 6) > len(raw_rets):
                    raise OverflowError(
                        "superflours decode for array: input " + str(len(raw_rets)) + \
                        " but expect at least " + str(64 + (ret_size << 1))
                    )
                return [
                    AbiDecoder.decode(ret_type[:-2], raw_rets[(idx << 6):(idx + 1) << 6])
                    for idx in range(1, ret_size + 1)
                ]
            else:
                print("TODO array-type:", ret_type)
                return

    @staticmethod
    def decodes(raw_rets, rets_type_list):
        if len(raw_rets) & MOD6:
            raise ValueError("data damaged")
        rets, ret_counter = [], 0

        for ret_type in rets_type_list:
            if AbiDecoder.is_array_type(ret_type):
                ret = AbiDecoder.decode_array(
                    ret_type,
                    raw_rets[(AbiDecoder.decode('uint256', raw_rets[ret_counter:ret_counter + 64]) << 1):]
                )
                rets.append(ret)
            else:
                ret = AbiDecoder.decode(ret_type, raw_rets[ret_counter:ret_counter + 64])
                rets.append(ret)
            ret_counter += 64
        return rets


if __name__ == '__main__':
    type_list = ['uint256', 'bytes2[]', 'bytes2[]', 'uint256', 'int256', 'bytes2[]']
    encodetest = AbiEncoder.encodes([123123, ['0x0142'], ['0x1420'], 1123, -1, ["0x1042"]], type_list)
    print("1234567890abcdef" * 0x30)  # 0x30 * 8 = 0x180
    print(encodetest)
    print(AbiDecoder.decodes(encodetest, type_list))
    print(AbiEncoder.encodes(['tannekawaii', 'daisuki'], ['string', 'string']))
    print(hex(INTM[32] - 2))
    print(AbiEncoder.encode('string', "tannekawaii"))
    print(AbiEncoder.encode('int256', -1))
    print(AbiEncoder.encode('int32', -1))
    print(AbiEncoder.encode('uint256', 1))
    print(AbiEncoder.encode('int32', 123))
    print(AbiEncoder.encode('byte', "0x01"))
    print(AbiEncoder.encode('bytes1', "0x01"))
    print(AbiEncoder.encode('bytes2', "0x0102"))
    print(AbiEncoder.encode('bytes3', "0x000102"))
    print(AbiEncoder.encode(
        'bytes',
        "0x000102030405060708090a0b0c0d0e0f000102030405060708090a0b0c0d0e0f000102030405060708090a0b0c0d0e0f0001020304" +
        "05060708090a0b0c0d0e0f"
    ))
