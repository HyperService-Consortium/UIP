from hexbytes import HexBytes
import rlp
# class EthDB(leveldb.LevelDB):
    # the child class of LevelDB

    # Get(key, verify_checksums=False, fill_cache=True): get value, raises KeyError if key not found
    # key: the query key

    # Put(key, value, sync=False): put key / value pair
    # key: the key
    # value: the value

    # Delete(key, sync=False): delete key / value pair, raises no error if key not found
    # key: the key

    # Write(write_batch, sync=False): apply multiple put / delete operations atomatically
    # write_batch: the WriteBatch object holding the operations

    # RangeIter(key_from = None, key_to = None, include_value = True,
    #           verify_checksums = False, fill_cache = True): return iterator
    # key_from: if not None: defines lower bound (inclusive) for iterator
    # key_to:   if not None: defined upper bound (inclusive) for iterator
    # include_value: if True, iterator returns key/value 2-tuples, otherwise, just keys

    # GetStats(): get a string of runtime information
    # Methods defined here:

    # CompactRange(...)
    # Compact keys in the range

    # CreateSnapshot(...)
    # create a new snapshot from current DB state

    # __init__(self, /, *args, **kwargs)
    # Initialize self.  See help(type(self)) for accurate signature.

    # def __init__(self, var):
    #     # var can be string of path or DB
    #     if isinstance(var, str):
    #         # create_if_missing=True
    #         # paranoid_checks=False
    #         leveldb.LevelDB.__init__(var, error_if_exists=True)
    #     elif isinstance(var, leveldb.LevelDB):
    #         pass
    #     else:
    #         raise TypeError("need path or LevelDB, But gets %s." % var.__name__)

    # __new__(*args, **kwargs) from builtins.type
    # Create and return a new object.  See help(type) for accurate signature.


# ethdb = plyvel.DB(ETHDB_PATH)#  error_if_exists=True)

def TransIntoHex(nodelist):
    decodelist = []
    for node in nodelist:
        if isinstance(node, list):
            decodelist.append(TransIntoHex(node))
        elif isinstance(node, bytes):
            decodelist.append(HexBytes(node).hex())
        else:
            raise TypeError("node must be str or list, But %s." % node.__name__)
    return decodelist


def decode(varlist):
    return TransIntoHex(rlp.decode(HexBytes(varlist)))
