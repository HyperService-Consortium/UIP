

# python modules

# ethereum modules
from hexbytes import HexBytes
from web3 import Web3

# uip modules
from uiputils.ethtools import ServiceStart
from dapp import DApp
from nsb import EthNetStatusBlockchain
from uiputils.ethtools.loc_cal import slicelocation

baser = DApp({
    'domain': "Ethereum://chain1",
    'name': "nsb",
    'passphrase': "123456"
})
# beiyong 0x92a875bff412aea7fab74daa1cba3f7b94415ac9
# beiyong 0x211939ec400c7391d45e97f4b547e0dbfb8905ee
nsb_addr = Web3.toChecksumAddress("0x15055c5173c91957ea49552bdee55487e3c2ac43")
# ("0x076122c56613fc1e3ae97d715ca7cb6a35a934c6")

nsb_abi_dir = '../contract/solidity/nsb/nsb.abi'
nsb_bytecode_dir = '../contract/solidity/nsb/nsb.bin'
nsb_db_dir = "../nsb/actiondata"
tx = {
    "from": Web3.toChecksumAddress(baser.info['http://127.0.0.1:8545']['address']),
    "gas": hex(400000)
}

if __name__ == '__main__':
    baser.unlockself()
    nsbt = EthNetStatusBlockchain(
        baser.info['http://127.0.0.1:8545']['address'],
        'http://127.0.0.1:8545',
        nsb_addr,
        nsb_abi_dir,
        "",
        tx,
        nsb_bytecode_dir=nsb_bytecode_dir
    )
    nsb = nsbt.handle
    print(nsb.funcs())
    handle = ServiceStart.startweb3('http://127.0.0.1:8545')
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

    update_func = nsbt.add_transaction_proposal('0x0C24884AEe4E89378Bb1E739A5c9b34834D384E5', 2, gasuse=hex(7999999))

    update_func.transact()
    print(update_func.loop_and_wait())

    print(nsbt.is_active_isc('0x0C24884AEe4E89378Bb1E739A5c9b34834D384E5'))

    print(nsbt.get_action('0x44fc96dc16bac02b59222b0e9f2019feb49f7fd2e092b8e3cf1a67db106fbd11'))
