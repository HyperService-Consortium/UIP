
# python modules

# uip modules
from uiputils.ethtools import FileLoad, JsonRPC
from ves import VerifiableExecutionSystem
from dapp import DApp
from uiputils.transaction import StateType
import time


# config
from uiputils.config import HTTP_HEADER, alice, bob, tom

from uiputils.loggers import console_logger

from py_nsbcli.modules.admin import set_admin_singleton_mode
set_admin_singleton_mode(False)

if __name__ == '__main__':
    # 029a
    tot_time = time.perf_counter()
    # prepare
    ves = VerifiableExecutionSystem()
    dapp_x = DApp(info_x)
    dapp_y = DApp(info_y)
    ves.appenduserlink([dapp_x, dapp_y])

    console_logger.info('{0} built, info:{1}'.format(dapp_x, dapp_x.info))
    console_logger.info('{0} built, info:{1}'.format(dapp_y, dapp_y.info))
    console_logger.info('{0} built, info:{1}'.format(ves, ves.__dict__))
