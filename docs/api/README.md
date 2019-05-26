UIP API Design

- ves
- nsb
- dapp
- uiputil
    -  **uip** types:
        - OpIntent
        - TransactionIntents
        - PaymentTransaction(Transaction)
        - InvokeTransaction(Transaction)
    - **uip** Chain DNS
    - **uip** Data parser
    - **tendermint**Data parser
    - **tendermint** json Encoder
    - **tendermint** json Decoder
    - **eth** types
        - Contract
        - EthPaymentTransaction(PaymentTransaction)
        - EthInvokeTransaction(InvokeTransaction)
    - **eth** ABI Encoder
    - **eth** ABI Decoder
    - **eth** Data parser
    - **eth** jsonRPC
    - **eth** SignatureVerifier
    - **solidity** types
        - SoliUint
        - SoliUint256
        - SoliUint128
        - SoliUint64
        - SoliUint32
        - SoliUin16
        - SoliUint8,
        - SoliInt
        - SoliInt256
        - SoliInt128
        - SoliInt64
        - SoliInt32
        - SoliIn16
        - SoliInt8
        - SoliBool
        - SoliAddress
        - SoliBytes
        - SoliString
    - **solidity** SliceLoc
    - **solidity** MapLoc

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

