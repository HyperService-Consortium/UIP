

import platform
from py_nsbcli import *
from py_nsbcli.modules.admin import get_admin
import py_nsbcli

from contract.tendermint.delegate.contract import DelegateContract


if platform.system() == "Windows":
    kvdb_path = "E:/project/go/src/github.com/Myriad-Dreamin/NSB/bin/kvstore"
else:
    kvdb_path = "/Users/zhuotaoliu/Development/HyperService//NSB/bin/kvstore"


def check_glo_db_is_ok():
    global glo_db
    if glo_db.handler_num < 0:
        print("the leveldb at ./kvstore open failed")
        exit(1)


def atexit_close_global_db():
    global glo_db
    glo_db.close()
    print("gracefully stop")


glo_db = py_nsbcli.LevelDB(kvdb_path)
check_glo_db_is_ok()

# modules
admin = get_admin("http://47.251.2.73:26657")
cli = Client(admin)
kvdb = KVDB(glo_db)
tom = kvdb.load_wallet("Tom")

opt = DelegateContract(cli)
print(opt.create_delegate(tom, [tom.address()], "Tom ABC", 666))


atexit_close_global_db()
