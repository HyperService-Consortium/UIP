

# python modules

# ethereum modules
from hexbytes import HexBytes
from web3 import Web3
# uip modules
from uiputils.ethtools import ServiceStart
from uiputils.uiptypes import DApp
from uiputils.nsb.nsb import EthNetStatusBlockchain
from uiputils.ethtools import slicelocation
baser = DApp({
    'domain': "Ethereum://chain1",
    'name': "nsb",
    'passphrase': "123456"
})
# beiyong 0x92a875bff412aea7fab74daa1cba3f7b94415ac9
nsb_addr = Web3.toChecksumAddress("0x822b41735c7f8f6cef522599f19df3bc3c2c55bf")
# ("0x076122c56613fc1e3ae97d715ca7cb6a35a934c6")

nsb_abi_dir = "../nsb/nsb.abi"
nsb_bytecode_dir = "../nsb/nsb.bin"
nsb_db_dir = "../nsb/actiondata"
tx = {
    "from": Web3.toChecksumAddress(baser.address),
    "gas": hex(400000)
}

if __name__ == '__main__':
    baser.unlockself()
    nsbt = EthNetStatusBlockchain(
        baser.address,
        baser.chain_host,
        nsb_addr,
        nsb_abi_dir,
        "",
        tx,
        nsb_bytecode_dir=nsb_bytecode_dir
    )
    nsb = nsbt.handle
    print(nsb.funcs())
    handle = ServiceStart.startweb3(baser.chain_host)
    print(HexBytes(handle.eth.getStorageAt(nsb_addr, slicelocation(10, 0, 1))).hex())
    # print(nsb.funct('getOwner', tx))
    # print(nsb.func('owners', 0))

    # test owner systems
    # # print(nsbt.get_owner())
    # print(nsbt.add_owner("0xe6c02eae01c5535b1657d039a1d9b284eb37046c"))
    # print(nsbt.is_owner("0xe6c02eae01c5535b1657d039a1d9b284eb37046c"))
    # # print(nsbt.get_owner())
    # print(nsbt.remove_owner("0xe6c02eae01c5535b1657d039a1d9b284eb37046c"))
    # print(nsbt.is_owner("0xe6c02eae01c5535b1657d039a1d9b284eb37046c"))
    # # print(nsbt.get_owner())

    print('waiting to verify [', nsbt.get_queue_l(), ',', nsbt.get_queue_r(), ')')

    update_func = nsbt.add_transaction_proposal('0xd722836602e9e2f576cabef8701bfa5b591192de', gasuse=hex(5000000))

    update_func.transact()
    print(update_func.loop_and_wait())

    print(nsbt.is_active_isc('0xd722836602e9e2f576cabef8701bfa5b591192de'))
