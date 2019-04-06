
# python modules
import time
from functools import partial

# ethereum modules
from hexbytes import HexBytes
from web3.utils.threads import Timeout as Web3Timeout

# eth modules
from uiputils.ethtools import JsonRPC, AbiEncoder, hex_match, hex_match_withprefix
from uiputils.errors import GenerationError


class ContractFunctionClass(object):
    # lazy contract-function
    @staticmethod
    def check_sig(function_sign: bytes or str) -> str:
        if isinstance(function_sign, bytes):
            function_sign = HexBytes(function_sign).hex()
        if hex_match_withprefix.match(function_sign):
            if len(function_sign) != 10:
                raise GenerationError("function signature must be 8 chars long (without prefix '0x')")
        elif hex_match.match(function_sign):
            if len(function_sign) != 8:
                raise GenerationError("function signature must be 8 chars long (without prefix '0x')")
            function_sign = "0x" + function_sign
        return function_sign

    @staticmethod
    def wait(host: str):

        def lazy_function(tx_resp: str, wait_time=25, query_period=1):
            tx_resp_json = JsonRPC.eth_get_transaction_receipt(tx_resp)
            expire_time = wait_time + time.time()
            while time.time() < expire_time:
                try:
                    resp = JsonRPC.send(tx_resp_json, rpc_host=host)
                    if resp['result'] is not None:
                        return resp
                    time.sleep(query_period)
                except Exception:
                    raise

        return lazy_function


class ContractFunction(ContractFunctionClass):
    # it will check function signature
    @staticmethod
    def transact(host, function_sign: str, function_args: list, function_args_type: list, tx: dict):

        def lazy_function():
            sig = ContractFunction.check_sig(function_sign)
            return JsonRPC.send(
                JsonRPC.eth_send_transaction(dict(
                    tx,
                    data=sig + AbiEncoder.encodes(function_args, function_args_type)
                )),
                rpc_host=host
            )['result']

        return lazy_function

    @staticmethod
    def call(host, function_sign: str, function_args: list, function_args_type: list,  tx: dict, tag="latest"):

        def lazy_function():
            sig = ContractFunction.check_sig(function_sign)
            return JsonRPC.send(
                JsonRPC.eth_call(
                    dict(tx, data=sig + AbiEncoder.encodes(function_args, function_args_type)),
                    tag
                ),
                rpc_host=host
            )['result']

        return lazy_function


class ContractFunctionWithoutCheck(ContractFunctionClass):
    # it won't check function signature
    @staticmethod
    def transact(host, function_sign: str, function_args: list, function_args_type: list):

        def lazy_function(transaction=None):
            if transaction is None:
                transaction = {}
            return JsonRPC.send(
                JsonRPC.eth_send_transaction(dict(
                    transaction,
                    data=function_sign + AbiEncoder.encodes(function_args, function_args_type)
                )),
                rpc_host=host
            )['result']

        return lazy_function

    @staticmethod
    def call(host, function_sign: str, function_args: list, function_args_type: list, tag="latest"):

        def lazy_function(transaction=None):
            if transaction is None:
                transaction = {}
            return JsonRPC.send(
                JsonRPC.eth_call(
                    dict(transaction, data=function_sign + AbiEncoder.encodes(function_args, function_args_type)),
                    tag
                ),
                rpc_host=host
            )['result']

        return lazy_function


class ContractFunctionClient(object):
    # lazy-function-client for Ethereum: web3.contract

    def __init__(
        self,
        function_transact=None,
        function_call=None,
        wait_catch=None,
        tx=None,
        timeout=25
    ):
        if function_transact is not None:
            self.transactor = partial(function_transact, transaction=tx)
        if function_call is not None:
            self.caller = partial(function_call, transaction=tx)

        self.wait_catch = wait_catch
        self.timeout = timeout
        self.tx_resp = None

    def transact(self):
        self.tx_resp = self.transactor()
        print('txresp', self.tx_resp)
        return self.tx_resp

    def call(self):
        self.tx_resp = self.caller()
        print('txresp', self.tx_resp)
        return self.tx_resp

    def wait(self, timeout=None):
        if self.tx_resp is None:
            raise LookupError("nothing to wait")
        if self.wait_catch is None:
            raise IndexError("catch-function doesn't exist")
        try:
            if timeout:
                return self.wait_catch(self.tx_resp, timeout)
            else:
                return self.wait_catch(self.tx_resp, self.timeout)
        except Web3Timeout:
            return None
        except Exception:
            raise

    def loop_and_wait(self):
        while True:
            try:
                tx_result = self.wait(timeout=998244353)
                if tx_result is not None:
                    return tx_result
            except Exception:
                raise


if __name__ == '__main__':
    print(ContractFunctionClass.check_sig('0x12345678'))
    print(ContractFunctionClass.check_sig(b'\x12\x34\x56\x78'))

    try:
        print(ContractFunctionClass.check_sig(123))
    except Exception as e:
        print(e)

    try:
        print(ContractFunctionClass.check_sig('2345678'))
    except Exception as e:
        print(e)

    try:
        print(ContractFunctionClass.check_sig('0x2345678'))
    except Exception as e:
        print(e)

