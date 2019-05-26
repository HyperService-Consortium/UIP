# UIP API Design

- [ves]()
- [nsb]()
- [dapp]()
- [uiputil](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#uiputils)
    -  **uip** types:
        - [OpIntent](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#opintent)
        - [TransactionIntents](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#transactionintents)
        - [Transaction](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#transaction)
        - [PaymentTransaction(Transaction)](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#paymenttransactiontransaction)
        - [InvokeTransaction(Transaction)](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#invoketransactiontransaction)
    -  **uip** [Chain DNS](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#chain-dns)
    -  **uip** [Data parser](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#data-parser)
    -  **tendermint** [Data parser](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#data-parser-2)
    -  **tendermint** [json Encoder](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#json-encoder)
    -  **tendermint** [json Decoder](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#json-decoder)
    -  **eth** types
        - [Contract](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#contract)
        - [EthPaymentTransaction(PaymentTransaction)](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#ethpaymenttransactionpaymenttransaction)
        - [EthInvokeTransaction(InvokeTransaction)](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#ethinvoketransactioninvoketransaction)
    -  **eth** [ABI Encoder](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#abi-encoder)
    -  **eth** [ABI Decoder](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#abi-decoder)
    -  **eth** [Data parser](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#data-parser-1)
    -  **eth** [jsonRPC]()
    -  **eth** [SignatureVerifier]()
    -  **solidity** types
        - [SoliUint](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#soliuint)
        - [SoliUint256](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#soliuint256)
        - [SoliUint128]()
        - [SoliUint64]()
        - [SoliUint32]()
        - [SoliUin16]()
        - [SoliUint8]()
        - [SoliInt]()
        - [SoliInt256]()
        - [SoliInt128]()
        - [SoliInt64]()
        - [SoliInt32]()
        - [SoliIn16]()
        - [SoliInt8]()
        - [SoliBool]()
        - [SoliAddress]()
        - [SoliBytes]()
        - [SoliString]()
    -  **solidity** [SliceLoc](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#sliceloc)
    -  **solidity** [MapLoc](https://github.com/HyperServiceOne/UIP/tree/master/docs/api#maploc)

# VES

###### \__init__

###### session_setup_prepare

###### session_setup_update

###### session_setup_finish

###### build_graph

##### send_txinfo_to_isc

###### insurance_claim

###### session_close

###### exec

# NSB

###### add_attestation

###### add_merkleproof

###### get_attestation

###### get_merkleproof

# DApp

###### ack_init

###### insurance_claim

###### exec

###### session_close_requset

# uiputils

#### OpIntent

###### \__init__(json)

###### @static create(json_array or json)

#### TransactionIntents

###### \__init__(op_intents: OpIntent, dependencies: json_array)

###### @property origin_intents

###### @property intents

###### @property belongs

###### @property dependencies

###### generate_from_opintents(op_intents)

###### sort(dependencies)

###### dictize()

###### jsonize()

###### hash()

#### Transaction

###### @property src

###### @property dst

###### @property meta

###### @property host

###### jsonize()

###### dictize()

#### PaymentTransaction(Transaction)

#### InvokeTransaction(Transaction)

###### @property parameters_description

#### Chain DNS

###### get_user_address(user_name, chain_type, chain_id)

###### get_user_address(user_name, chain_type://chain_id)

###### get_relay_address(chain_type, chain_id)

###### get_relay_address(chain_type://chain_id)

###### get_host(chain_type, chain_id)

###### get_host(chain_type://chain_id)

#### Data Parser

###### parse(args: list, args_desc: list, chain_type)

# uiputils.eth

## contract

###### call(function_name, args...)

###### transact(function_name, args...)

###### lazy_transact(function_name, args…, timeout)

#### EthPaymentTransaction(PaymentTransaction)

#### EthInvokeTransaction(InvokeTransaction)

#### ABI Encoder

###### encode(arg: any, arg_desc: string)

###### encodes(args: list, args_desc: list)    

#### ABI Decoder    

###### decode(ret_bytes: bytes, ret_desc: string)

###### decodes(ret_bytes: bytes, rets_desc: list)

###### decode_string(ret_bytes: str, ret_desc: string)

###### decodes_string(ret_bytes: str, rets_desc: list)    

#### Data parser

###### parse(args: list, args_desc: list)

#### Json RPC

###### rpc_apis()

###### get_json(api_name, args)

###### api_name(args)

#### Signature Verifier

###### verify_by_raw_message(signature, msg, address)

###### verify_by_hashed_message(signature, msg, address)

# uiputils.tendermint

#### Data parser

###### parse(args: list, args_desc: list)

#### json Encoder

#### json Decoder

# uiputils.solidity

#### SoliUint

__init__(num)

###### encode()

###### @static decode(raw_bytes: str or bytes)

###### loc(slot)

###### keccak(slot)

###### ori_loc(slot)

#### SoliUint256

Same as **SoliUint**

#### SliceLoc

#### MapLoc

