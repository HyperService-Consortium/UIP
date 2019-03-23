pragma solidity ^0.4.22;

interface NetworkStatusBlockChain {
    function validMerkleProoforNot(bytes32) external returns(bool);
}

contract InsuranceSmartContract {
    uint constant public MAX_OWNER_COUNT = 50;
    uint constant public MAX_VALUE_PROPOSAL_COUNT = 5;
    // bytes constant public ETH_PREFIX = hex"19457468657265756d205369676e6564204d6573736167653a0a";
    
    enum State {
        unknown,
        init,
        inited,
        open,
        opened,
        closed
    }

    struct TransactionState {
        State state;
        uint256 topen;
        uint256 tclose;
        bytes32[] results;
    }
    
    struct Transaction {
        address fr;
        address to;
        uint seq;
        uint amt;
        bytes rlpedMeta;
        // mapping(string => string) meta;
        // string[] field;
    }
	
	bool public iscOpened;
	bool public iscClosed;
	bool public iscSettled;
	
    mapping (address => uint256) public ownerRequiredFunds;
    mapping (address => uint256) public ownerFunds;
    
    
    address[] public owners;
    mapping (address => bool) public isOwner;

    uint256 public remainingFund;

    Transaction[] public txInfo;
    
    TransactionState[] public txState;

    bytes public rlpedTxIntent;
    bytes32 public vesack;
    mapping (address => bytes) public acks;
    mapping (address => bool) public ownerAck;
    uint public acked;
    
    modifier onlyOwner()
    {
        require(isOwner[msg.sender], "owner doesn't exist.");
        _;
    }
    
    modifier iscInitializing()
    {
        require(iscOpened == false, "ISC is initialized");
        require(iscClosed == false, "ISC is ended");
        _;
    }
    
    modifier iscOpening()
    {
        require(iscOpened, "ISC is initializing");
        require(iscClosed == false, "ISC closed");
        _;
    }
    
    modifier iscActive()
    {
        require(iscClosed == false, "ISC closed");
        _;
    }
    
    modifier validUploader()
    {
        require(msg.sender == owners[0], "you have no access to update the TxInfo");
        _;
    }
    
    /**********************************************************************
     *                           Initialize Period                        *
     **********************************************************************/
    
    constructor (
        address[] iscowners,
        uint[] funds,
        bytes signContent,
        bytes signature,
        bytes32 keccaksignature,
        uint256 txCount
        //bytes32[] transaction_content
    )
        public
        payable
    {
        // require(msg.sender == iscowners[0], "iscowners[0] must be the sender");
        // require(msg.value >= ownerRequiredFunds[msg.sender], "no enough fund");
        // ownerFunds[msg.sender] = msg.value;
        //msg.sender.transfer(msg.value);
        
        uint idx;
        
        iscOpened = iscClosed = iscSettled = false;
        txInfo.length = txCount;
        txState.length = txCount;
        
        bytes32 keccakhash = keccak256(signContent);
        require(validateSignatrue(signature, keccakhash) == iscowners[0], "wrong signature");
        rlpedTxIntent = signContent;
        acks[iscowners[0]] = signature;
        vesack = keccaksignature;
        acked = 1;
        
        for(idx = 0; idx < iscowners.length; idx++) {
            require(!isOwner[iscowners[idx]] && iscowners[idx] != 0, "owner exists or its address is invalid");
            isOwner[iscowners[idx]] = true;
            ownerRequiredFunds[iscowners[idx]] = funds[idx];
        }
        owners = iscowners;
        
        
        
        // uint idx;
        // uint idy;
        // uint bse;
        // uint meta_length;
        // txInfo.length++;
        // Transaction storage to_Add = txInfo[0];
        // txState.length++;
        // for(idx = 0; idx < owners.length; idx++)
        // {
        //     require(!isowner[owners[idx]] && owners[idx] != 0, "owner exists or its address is invalid");
        //     ownerfunds[owners[idx]] = funds[idx];
        // }
        
        
        // for(idx = 0; ; )
        // {
        //     bse = idx + 4;
        //     require(bse <= transaction_content.length, "invalid transaction base info");
        //     to_Add.fr = bytes32ToAddress(transaction_content[idx]);
        //     to_Add.to = bytes32ToAddress(transaction_content[idx + 1]);
        //     to_Add.seq = uint(transaction_content[idx + 2]);
        //     meta_length = uint(transaction_content[idx + 3]);
        //     to_Add.field.length = meta_length;
        //     meta_length <<= 1;
        //     require(bse + meta_length <= transaction_content.length, "invalid transaction meta_length");
        //     for(idy = 0; idy < meta_length; idy += 2)
        //     {
        //         to_Add.field[idx >> 1] = bytes32ToString(transaction_content[bse + idy]);
        //         to_Add.meta[to_Add.field[idx >> 1]] = bytes32ToString(transaction_content[bse + idy + 1]);
        //     }
        //     idx = bse + meta_length;
        //     if(idx == transaction_content.length) break;
        //     txInfo.length++;
        //     txState.length++;
        //     to_Add = txInfo[txInfo.length - 1];
        //     //test.push(bytes32ToString(transaction_content[idy]));
        // }
    }
    
    function updateTxInfo(
        uint idx,
        address fr,
        address to,
        uint seq,
        uint amt,
        bytes rlpedMeta
    )
        public
        iscInitializing
        validUploader
    {
        require(idx < txInfo.length, "idx overflow");
        txInfo[idx] = Transaction(fr, to, seq, amt, rlpedMeta);
    }
    
    function updateTxFr(uint idx, address fr)
        public
        iscInitializing
        validUploader
    {
        require(idx < txInfo.length, "idx overflow");
        txInfo[idx].fr = fr;
    }
    
    function updateTxTo(uint idx, address to)
        public
        iscInitializing
        validUploader
    {
        require(idx < txInfo.length, "idx overflow");
        txInfo[idx].to = to;
    }
    
    function updateTxSeq(uint idx, uint seq)
        public
        iscInitializing
        validUploader
    {
        require(idx < txInfo.length, "idx overflow");
        txInfo[idx].seq = seq;
    }
    
    function updateTxAmt(uint idx, uint amt)
        public
        iscInitializing
        validUploader
    {
        require(idx < txInfo.length, "idx overflow");
        txInfo[idx].amt = amt;
    }
    
    function updateTxRlpedMeta(uint idx, bytes rlpedMeta)
        public
        iscInitializing
        validUploader
    {
        require(idx < txInfo.length, "idx overflow");
        txInfo[idx].rlpedMeta = rlpedMeta;
    }
    
    function userAck(bytes signature)
        public
        payable
        iscInitializing
        onlyOwner
    {
        require(validateSignatrue(signature, vesack) == msg.sender, "wrong signature");
        require(ownerAck[msg.sender] == false, "updated");
        require(msg.value >= ownerRequiredFunds[msg.sender], "no enough fund");
        
        // msg.sender.transfer(msg.value);
        
        acks[msg.sender] = signature;
        ownerAck[msg.sender] =true;
        acked++;
        if (acked == owners.length) {
            iscOpened = true;
        }
    }
    
    function userRefuse()
        public
        iscInitializing
        onlyOwner
    {
        iscClosed = true;
        iscSettled = true;
    }
     
    /**********************************************************************
     *                             Active Period                          *
     **********************************************************************/
    
    // function insuranceClaim()
    
    function ChangeState(uint tid, uint state)
        public
        onlyOwner
        iscOpening
    {
        require(tid < txState.length, "invalid tid");
        require(state < 6, "invalid state");
        require(state > uint(txState[tid].state), "require more advanced state");
        txState[tid].state = State(state);
    }
    
    function ChangeStateOpened(uint tid, uint topen)
        public
        onlyOwner
        iscOpening
    {
        State state = State.opened;
        require(tid < txState.length, "invalid tid");
        require(uint(state) <= 6, "invalid state");
        require(uint(state) > uint(txState[tid].state), "require more advanced state");
        txState[tid].state = State(state);
        txState[tid].topen = topen;
    }
    
    function ChangeStateClosed(uint tid, uint tclose)
        public
        onlyOwner
        iscOpening
    {
        State state = State.closed;
        require(tid < txState.length, "invalid tid");
        require(uint(state) <= 6, "invalid state");
        require(uint(state) > uint(txState[tid].state), "require more advanced state");
        txState[tid].state = State(state);
        txState[tid].tclose = tclose;
    }
    
    function ChangeResult(NetworkStatusBlockChain nsb, uint tid, bytes32[] results)
        public
        onlyOwner
        iscOpening
    {
        require(tid < txState.length, "invalid tid");
        require(txState[tid].state == State.open, "only open-state transaction can be modified");
        for (uint idx=0; idx < results.length; idx++) {
            require(nsb.validMerkleProoforNot(results[idx]) == true, "invalid MerkleProof in results");
        }
        txState[tid].results = results;
    }
    
    function StopISC()
        public
        onlyOwner
        iscOpening
    {
        iscClosed = true;
    }
     
    /**********************************************************************
     *                          Settle Period                             *
     **********************************************************************/
     
    function settleContract()
        public
        onlyOwner
    {
        require(iscClosed, "ISC is active now");
        iscSettled = true;
    }
    
    function returnFunds()
        public
        onlyOwner
    {
        require(iscSettled, "ISC hasn't been settled yet");
        uint funds = ownerFunds[msg.sender];
        ownerFunds[msg.sender] = 0;
        msg.sender.transfer(funds);
    }
    
    /**********************************************************************
     *                               others                               *
     **********************************************************************/
     
    function getMetaByNumber(uint tid)
        public
        view
        returns (bytes)
    {
        require(tid < txInfo.length, "tid overflow");
        return txInfo[tid].rlpedMeta;
    }

    function getState(uint tid)
        public
        view
        returns (State)
    {
        require(tid < txState.length, "tid overflow");
        return txState[tid].state;
    }
    
    function getResult(uint tid)
        public
        view
        returns (bytes32[])
    {
        require(tid < txState.length, "tid overflow");
        return txState[tid].results;
    }
    
    function getTransactionInfo(uint tid)
        public
        view
        returns (
            address fr,
            address to,
            uint seq,
            uint amt,
            bytes rlpedMeta
        )
    {
        require(tid < txState.length, "tid overflow");
        Transaction storage toGet = txInfo[tid];
        fr = toGet.fr;
        to = toGet.to;
        seq = toGet.seq;
        amt = toGet.amt;
        rlpedMeta = toGet.rlpedMeta;
    }
    
    function stakeFund()
        public
        payable
        onlyOwner
        iscActive
    {
        remainingFund = safeAdd(remainingFund, msg.value);
    }
    
    function isTransactionOwner(address queryaddr, uint tid)
        public
        view
        returns (bool)
    {
        require(tid < txState.length, "tid overflow");
        return queryaddr == txInfo[tid].fr;
    }
    
    function isRawSender(address queryaddr)
        public
        view
        returns (bool)
    {
        return queryaddr == owners[0];
    }
    
    function txInfoLength()
        public
        view
        returns (uint)
    {
        return txInfo.length;
    }
    
    function getTxInfoHash(uint tid)
        public
        view
        returns (bytes32)
    {
        require(tid < txState.length, "tid overflow");
        return keccak256(
            txInfo[tid].fr,
            txInfo[tid].to,
            txInfo[tid].seq,
            txInfo[tid].amt,
            txInfo[tid].rlpedMeta
        );
    }
    
    function closed()
        public
        view
        returns (bool)
    {
        return iscClosed;
    }
    
    /**********************************************************************
     *                             SafeCalc                               *
     **********************************************************************/
    
    function safeMul(uint256 a, uint256 b)
        internal
        pure
        returns (uint256)
    {
        uint256 c = a * b;
        assert(a == 0 || c / a == b);
        return c;
    }

    function safeDiv(uint256 a, uint256 b)
        internal
        pure
        returns (uint256)
    {
        assert(b > 0);
        uint256 c = a / b;
        assert(a == b * c + a % b);
        return c;
    }

    function safeSub(uint256 a, uint256 b)
        internal
        pure
        returns (uint256)
    {
        assert(b <= a);
        return a - b;
    }

    function safeAdd(uint256 a, uint256 b)
        internal
        pure
        returns (uint256)
    {
        uint256 c = a + b;
        assert(c >= a);
        return c;
    }
    
    /**********************************************************************
     *                              Caster                                *
     **********************************************************************/
    
    function bytes32ToAddress(bytes32 x) public pure returns (address) {
        return address(uint160(bytes20(x)));
    }

    function bytes32ToString(bytes32 x) public pure returns (string) {
        bytes memory bytesString = new bytes(32);
        uint charCount = 0;
        for (uint j = 0; j < 32; j++) {
            byte char = byte(bytes32(uint(x) * 2 ** (8 * j)));
            if (char != 0) {
                bytesString[charCount] = char;
                charCount++;
            }
        }
        bytes memory bytesStringTrimmed = new bytes(charCount);
        for (j = 0; j < charCount; j++) {
            bytesStringTrimmed[j] = bytesString[j];
        }
        return string(bytesStringTrimmed);
    }
    
    function slice(bytes memory data,uint start,uint len)
        public
        pure
        returns(bytes)
    {
        bytes memory b=new bytes(len);
        for(uint i=0;i<len;i++)
        {
            b[i]=data[i+start];
        }
        return b;
    }
    
    function bytesToBytes32(bytes memory source)
        public
        pure
        returns(bytes32 result)
    {
        assembly{
        result :=mload(add(source,32))
        }
    }
    
    /**********************************************************************
     *                               Crypto                               *
     **********************************************************************/
     
     function validateSignatrue(bytes memory signature, bytes32 msghash)
        public
        pure
        returns (address)
    {
        bytes32 r = bytesToBytes32(slice(signature,0,32));
        bytes32 s = bytesToBytes32(slice(signature,32,32));
        byte v = slice(signature,64,1)[0];
        return ecrecoverDecode(msghash, r, s, v);
      
    }
    
    function ecrecoverDecode(bytes32 msghash,bytes32 r,bytes32 s, byte v1)
        public
        pure
        returns(address addr)
    {
        uint8 v=uint8(v1);
        if(v<=1)
        {
            v += 27;
        }
        addr=ecrecover(msghash, v, r, s);
    }
}
