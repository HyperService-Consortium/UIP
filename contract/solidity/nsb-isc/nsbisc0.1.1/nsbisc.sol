pragma solidity ^0.5.0;

interface InsuranceSmartContractInterface {
    
    function isRawSender(address) external view returns(bool);
    
    function txInfoLength() external view returns(uint);
    
    function getTxInfoHash(uint) external view returns(bytes32);
    
    function isTransactionOwner(address, uint) external view returns(bool);
    
    function closed()  external view returns(bool);
}


interface NetworkStatusBlockChainInterface {
    function validMerkleProoforNot(bytes32)  external view returns(bool);
}

contract InsuranceSmartContract is InsuranceSmartContractInterface {
    /**********************************************************************/
    // constant
    uint constant public MAX_OWNER_COUNT = 50;
    uint constant public MAX_VALUE_PROPOSAL_COUNT = 5;
    
    /**********************************************************************
     *                               Structs                              *
     **********************************************************************/

    // Enumeration of Transaction State
    enum State {
        // 0
        unknown,
        // 1
        init,
        // 2
        inited,
        // 3
        open,
        // 4
        opened,
        // 5
        closed
    }
    
    enum ISCState {
        // 0
        init,
        // 1
        inited,
        // 2
        opening,
        // 3
        settling,
        // 4
        closed
    }
    
    struct TransactionState {
        State state;
        // Transaction's open-time
        uint256 topen;
        // Transaction's close-time
        uint256 tclose;
        // result of Transactions (MerkleProofHashes storaged on NSB)
        bytes32[] results;
    }
    
    struct Transaction {
        // from address
        address fr;
        // to address (Optional)
        address to;
        // unique seq (serial)
        uint seq;
        // meta.amt
        uint amt;
        
        // rlpedMetadata
        // [[key1, value1], [key2, value2], ...]
        // e.g., [['amt', '1000'], ['comment', 'Here is an Example Rlped Meta Data']]
        bytes rlpedMeta;
        // mapping(string => string) meta;
        // string[] field;
    }
    
    ISCState public iscState;
    
    // minimum fund an owner should stake
    mapping (address => uint256) public ownerRequiredFunds;
    // amount of fund an owner staked
    mapping (address => uint256) public ownerFunds;
    
    // the isc users (including VES's account)
    address[] public owners;
    // whether an account is owner of isc or not
    mapping (address => bool) public isOwner;

    // Transactions information
    Transaction[] public txInfo;
    // Transactions status
    TransactionState[] public txState;

    // complete rlp-serialized Transaction content
    // [session-id, txs-intent as json]
    bytes public rlpedTxIntent;
    
    // vesack = keccak256(
    //    bytes('\x19Ethereum Signed Message:\n'),
    //    bytes('130'),
    //    bytes(hexstring of Sig_VES)
    //)
    bytes32 public vesack;
    
    // Sigs of owners
    mapping (address => bytes) public acks;
    // whether an owner acknowledged or not
    mapping (address => bool) public ownerAck;
    // the number of acknowledged owners
    uint public acked;
    uint public frozenTx;
    
    modifier onlyOwner()
    {
        require(isOwner[msg.sender], "owner doesn't exist.");
        _;
    }
    
    modifier iscInitializing()
    {
        require(iscState == ISCState.init, "ISC is initialized or waiting acks  ");
        _;
    }
    
    modifier iscOpening()
    {
        require(iscState != ISCState.init && iscState != ISCState.inited, "ISC is initializing");
        require(iscState == ISCState.opening, "ISC closed");
        _;
    }
    
    modifier iscActive()
    {
        require(iscState != ISCState.closed && iscState != ISCState.settling, "ISC closed");
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
        address[] memory iscowners,
        uint[] memory funds,
        bytes memory signContent,
        bytes memory signature,
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
        
        iscState = ISCState.init;
        frozenTx = 0;
        txInfo.length = txCount;
        txState.length = txCount;
        
        bytes32 keccakhash = keccak256(signContent);
        require(validateSignatrue(signature, keccakhash) == iscowners[0], "wrong signature");
        rlpedTxIntent = signContent;
        acks[iscowners[0]] = signature;
        ownerAck[iscowners[0]] = true;
        vesack = keccaksignature;
        acked = 1;
        
        for(idx = 0; idx < iscowners.length; idx++) {
            require(!isOwner[iscowners[idx]] && iscowners[idx] != address(0), "owner exists or its address is invalid");
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
        bytes memory rlpedMeta
    )
        public
        iscInitializing
        validUploader
    {
        require(idx < txInfo.length, "idx overflow");
        require(txState[idx].state == State.unknown, "this transaction's information is frozen");
        txInfo[idx] = Transaction(fr, to, seq, amt, rlpedMeta);
    }
    
    // function updateTxFr(uint idx, address fr)
    //     public
    //     iscInitializing
    //     validUploader
    // {
    //     require(idx < txInfo.length, "idx overflow");
    //     require(txState[idx].state == State.unknown, "this transaction's information is frozen");
    //     txInfo[idx].fr = fr;
    // }
    
    // function updateTxTo(uint idx, address to)
    //     public
    //     iscInitializing
    //     validUploader
    // {
    //     require(idx < txInfo.length, "idx overflow");
    //     require(txState[idx].state == State.unknown, "this transaction's information is frozen");
    //     txInfo[idx].to = to;
    // }
    
    // function updateTxSeq(uint idx, uint seq)
    //     public
    //     iscInitializing
    //     validUploader
    // {
    //     require(idx < txInfo.length, "idx overflow");
    //     require(txState[idx].state == State.unknown, "this transaction's information is frozen");
    //     txInfo[idx].seq = seq;
    // }
    
    // function updateTxAmt(uint idx, uint amt)
    //     public
    //     iscInitializing
    //     validUploader
    // {
    //     require(idx < txInfo.length, "idx overflow");
    //     require(txState[idx].state == State.unknown, "this transaction's information is frozen");
    //     txInfo[idx].amt = amt;
    // }
    
    // function updateTxRlpedMeta(uint idx, bytes rlpedMeta)
    //     public
    //     iscInitializing
    //     validUploader
    // {
    //     require(idx < txInfo.length, "idx overflow");
    //     require(txState[idx].state == State.unknown, "this transaction's information is frozen");
    //     txInfo[idx].rlpedMeta = rlpedMeta;
    // }
    
    function freezeInfo(uint idx)
        public
        iscInitializing
        validUploader
    {
        require(idx < txInfo.length, "idx overflow");
        if(txState[idx].state == State.unknown) {
            txState[idx].state = State.init;
            frozenTx++;
            if(frozenTx == txInfo.length) {
                iscState = ISCState.inited;
            }
        }
    }
    
    function userAck(bytes memory signature)
        public
        payable
        onlyOwner
    {
        require(iscState == ISCState.inited, "ISC is opened or waiting initializing");
        require(validateSignatrue(signature, vesack) == msg.sender, "wrong signature");
        require(ownerAck[msg.sender] == false, "updated");
        require(msg.value >= ownerRequiredFunds[msg.sender], "no enough fund");
        
        // msg.sender.transfer(msg.value);
        
        acks[msg.sender] = signature;
        ownerAck[msg.sender] =true;
        acked++;
        if (acked == owners.length) {
            iscState = ISCState.opening;
        }
    }
    
    function userRefuse()
        public
        onlyOwner
    {
        require(iscState == ISCState.inited, "ISC is opened or waiting initializing");
        iscState = ISCState.settling;
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
    
    function ChangeResult(address nsb_addr, uint tid, bytes32[] memory results)
        public
        onlyOwner
        iscOpening
    {
        NetworkStatusBlockChainInterface nsb = NetworkStatusBlockChainInterface(nsb_addr);
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
        iscState = ISCState.settling;
    }
     
    /**********************************************************************
     *                          Settle Period                             *
     **********************************************************************/
     
    function settleContract()
        public
        onlyOwner
    {
        require(iscState == ISCState.settling, "ISC is active now");
        iscState = ISCState.closed;
    }
    
    function returnFunds()
        public
        onlyOwner
    {
        require(iscState == ISCState.closed, "ISC hasn't been settled yet");
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
        returns (bytes memory)
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
        returns (bytes32[] memory)
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
            bytes memory rlpedMeta
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
        ownerFunds[msg.sender] = safeAdd(ownerFunds[msg.sender], msg.value);
    }
    
    function isTransactionOwner(address queryaddr, uint tid)
        external
        view
        returns (bool)
    {
        require(tid < txState.length, "tid overflow");
        return queryaddr == txInfo[tid].fr;
    }
    
    function isRawSender(address queryaddr)
        external
        view
        returns (bool)
    {
        return queryaddr == owners[0];
    }
    
    function txInfoLength()
        external
        view
        returns (uint)
    {
        return txInfo.length;
    }
    
    function getTxInfoHash(uint tid)
        external
        view
        returns (bytes32)
    {
        require(tid < txState.length, "tid overflow");
        return keccak256(abi.encodePacked(
            txInfo[tid].fr,
            txInfo[tid].to,
            txInfo[tid].seq,
            txInfo[tid].amt,
            txInfo[tid].rlpedMeta
        ));
    }
    
    function closed()
        external
        view
        returns (bool)
    {
        return iscState == ISCState.closed;
    }
    
    /**********************************************************************
     *                             SafeCalc                               *
     **********************************************************************/


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

    function bytes32ToString(bytes32 x) public pure returns (string memory) {
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
        for (uint j = 0; j < charCount; j++) {
            bytesStringTrimmed[j] = bytesString[j];
        }
        return string(bytesStringTrimmed);
    }
    
    function slice(bytes memory data,uint start,uint len)
        public
        pure
        returns(bytes memory)
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

contract NetworkStatusBlockChain is NetworkStatusBlockChainInterface {
    /**********************************************************************/
    // constant
    
    uint constant public MAX_OWNER_COUNT = 50;
    uint constant public MAX_VALUE_PROPOSAL_COUNT = 5;
    
    /**********************************************************************
     *                               Structs                              *
     **********************************************************************/
    
    struct MerkleProof {
        string blockaddr;
        // storage roothash
        bytes32 storagehash;
        // storaged key
        bytes32 key;
        // corresponding value
        bytes32 value;
    }

    struct Action {
        // Party a
        // address pa;
        // Party z
        // address pz;
        // signature
		bytes32 msghash;
        bytes signature;
    }
    
    struct Transaction {
		// transaction content hash
		bytes32 txhash;
		// Actions' hash
		bytes32[] actionHash;
		// MerkleProofs' hash
		bytes32[] proofHash;
	}

	struct Transactions {
		// related contract_address (ISC) // if it necessary to defining as InsuranceSmartContract
		address contract_addr;
		// trnasactions' state
		Transaction[] txInfo; 
	}
    
    /**********************************************************************
     *                              Storage                               *
     **********************************************************************/
    // MerkleProof System Storage
    
    // The MerkleProofTree
    // keccak256(string + storagehash + key + value) maps to MerkleProof
    bytes32[] public waitingVerifyProof; // slot 0
    // corresponding valid votes' number
    uint32[] public validCount; // slot 1
    // corresponding votes' number
    uint32[] public votedCount; // slot 2
    // keccakhash of MerkleProof mapsto index of MerkleProof in waitingVerifyProof
    mapping (bytes32 => uint32) public proofPointer; // slot 3
    // if owner voted
    mapping (address => mapping (bytes32 => bool)) public ownerVoted; // slot 4
    // remained verifying MerkleProofs range [votedPointer, waitingVerifyProof.length)
    uint32 public votedPointer; // slot 5

    // all the MerkleProofs on the contract
    mapping (bytes32 => MerkleProof) public MerkleProofTree; // slot 6
    // if the MerkleProof Atte is valid, verifiedMerkleProof[Atte] == true
    mapping (bytes32 => bool) public verifiedMerkleProof; // slot 7

    /**********************************************************************/
    // Action System Storage
    
    // ActionTree (keccak256(Action) => Action)
    mapping (bytes32 => Action) public ActionTree; // slot 8
    
    /**********************************************************************/
    // Owner System Storage
    
    // The Net State BlockChain(NSB) contract is owned by multple entities to ensure security.
    mapping (address => bool) public isOwner; // slot 9
    address[] public owners; // slot 10

    uint public requiredOwnerCount; // slot 11
    uint public requiredValidVotesCount; // slot 12

    // Maps used for adding and removing owners.
    mapping (address => mapping (address => bool)) public addingOwnerProposal; // slot 13
    mapping (address => mapping (address => bool)) public removingOwnerProposal; // slot 14
    
    /**********************************************************************/
    // Transaction System Storage
    
	Transactions[] public txsStack; // slot 15
	mapping (address => Transactions) public txsReference; // slot 16
	mapping (address => bool) public activeISC; // slot 17
	mapping (bytes32 => address) public proofHashCallback; // slot 18
    
    /**********************************************************************
     *                      event & condition                             *
     **********************************************************************/
    
    event addingMerkleProof(string, bytes32, bytes32, bytes32);


    modifier ownerDoesNotExist(address owner) {
        require(!isOwner[owner], "owner exists");
        _;
    }

    modifier ownerExists(address owner) {
        require(isOwner[owner], "onwer does not exist");
        _;
    }

    modifier validRequirement(uint ownerCount, uint _requiredOwner) {
        require(ownerCount < MAX_OWNER_COUNT, "too many owners");
        require(_requiredOwner <= ownerCount, "not enough owners");
        require(_requiredOwner != 0, "at least one positive voter");
        require(ownerCount != 0, "at least one owner");
        _;
    }

    modifier validMerkleProof(bytes32 storagehash, bytes32 key) {
        require(storagehash != 0, "invalid storagehash");
        require(key != 0, "invalid key");
        _;
    }

    modifier remainMerkleProof(uint curPointer) {
        require(curPointer < waitingVerifyProof.length, "no MerkleProof to fetch");
        _;
    }

    modifier validVoteByHash(address addr, bytes32 keccakhash) {
        require(MerkleProofTree[keccakhash].storagehash != bytes32(0),
            "The MerkleProof is not in MerkleProofTree");
        require(verifiedMerkleProof[keccakhash] == false, "the MerkleProof is proved");
        require(ownerVoted[addr][keccakhash] == false, "you voted this MerkleProof");
        // require(curVotedPointer < ownersPointer[addr], "no MerkleProof to vote");
        // require(waitingVerifyProof[curVotedPointer] != 0, "the MerkleProof is proved");
        _;
    }

    modifier validVoteByPointer(address addr, uint32 curPointer) {
        require(curPointer < waitingVerifyProof.length, "the pointer is too large");
        require(votedPointer <= curPointer, "the pointer is too small");

        bytes32 keccakhash = waitingVerifyProof[curPointer];

        require(keccakhash != 0, "the MerkleProof is proved");

        require(ownerVoted[addr][keccakhash] == false, "you voted this MerkleProof");
        _;
    }

    // Remember to specify at least one address and set the _required as one.
    constructor (address[] memory _owners, uint _required)
        public
        // validRequirement(_owners.length, _required)
    {
        for (uint i = 0; i<_owners.length; i++) {
            require(!isOwner[_owners[i]] && _owners[i] != address(0), "owner exists or its address is invalid");
            isOwner[_owners[i]] = true;
            owners.push(_owners[i]);
        }
        
        requiredOwnerCount = _required;
        requiredValidVotesCount = _required;
    }

    /**********************************************************************
     *                            Owner System                            *
     **********************************************************************/

    function addOwner(address _newOwner)
        public
        ownerExists(msg.sender)
        validRequirement(owners.length + 1, requiredOwnerCount)
    {
        require(_newOwner != address(0), "invalid owner address");
        addingOwnerProposal[_newOwner][msg.sender] = true;

        //use a integer to count it?
        uint vote_count = 0;
        for (uint i = 0; i < owners.length; i++) {
            address owner = owners[i];
            if (addingOwnerProposal[_newOwner][owner] == true) {
                vote_count ++;
            }
        }

        // Adding owner proposal is approved.
        if (vote_count >= requiredOwnerCount) {
            owners.push(_newOwner);
            isOwner[_newOwner] = true;
        }
    }

    function removeOwner(address _removeOwner)
        public
        ownerExists(msg.sender)
        ownerExists(_removeOwner)
        validRequirement(owners.length - 1, requiredOwnerCount)
    {
        removingOwnerProposal[_removeOwner][msg.sender] = true;

        //use a integer to count it?
        uint vote_count = 0;
        for (uint i = 0; i < owners.length; i++) {
            address owner = owners[i];
            if (removingOwnerProposal[_removeOwner][owner] == true) {
                vote_count ++;
            }
        }

        // Removing owner proposal is approved.
        if (vote_count >= requiredOwnerCount) {
            isOwner[_removeOwner] = false;
            for (uint j = 0; j < owners.length; j++) {
                if (owners[j] == _removeOwner) {
                    owners[j] = owners[owners.length - 1];
                    break;
                }
            }
            owners.length -= 1;
        }
    }

    function getOwner()
        public
        view
        ownerExists(msg.sender)
        returns (address[] memory)
    {
        return owners;
    }

    function getOwnerCount()
        public
        view
        returns (uint)
    {
        return owners.length;
    }

    function isSenderAOwner()
        public
        view
        returns (bool)
    {
        return isOwner[msg.sender];
    }

    /**********************************************************************
     *                     MerkleProof Storage System                     *
     **********************************************************************/

    // change it to VES/DAPP/NSB user?
    function addMerkleProof(string memory blockaddr, bytes32 storagehash, bytes32 key, bytes32 val)
        public
        ownerExists(msg.sender)
        validMerkleProof(storagehash, key)
    {
        MerkleProof memory toAdd = MerkleProof(blockaddr, storagehash, key, val);
        bytes32 keccakhash = keccak256(abi.encodePacked(blockaddr, storagehash, key, val));

        require(MerkleProofTree[keccakhash].storagehash == 0, "already in MerkleProofTree");

        proofPointer[keccakhash] = uint32(waitingVerifyProof.length);
        waitingVerifyProof.push(keccakhash);
        MerkleProofTree[keccakhash] = toAdd;
        validCount.length ++;
        votedCount.length ++;

        emit addingMerkleProof(blockaddr, storagehash, key, val);
    }

    function voteProofByHash(bytes32 keccakhash, bool validProof)
        public
        ownerExists(msg.sender)
        validVoteByHash(msg.sender, keccakhash)
    {
        uint32 curPointer = proofPointer[keccakhash];

        //update counts
        if(validProof) {
            validCount[curPointer] ++;
        }
        votedCount[curPointer] ++;

        //judge if there is enough owners voted
        if (votedCount[curPointer] == requiredOwnerCount) {
            if (validCount[curPointer] >= requiredValidVotesCount) {
                verifiedMerkleProof[keccakhash] = true;
            } else {
                delete MerkleProofTree[keccakhash];
            }
            delete waitingVerifyProof[curPointer];
            delete validCount[curPointer];
            delete votedCount[curPointer];
        }

        //update the pointer
        while(votedPointer < waitingVerifyProof.length &&
            waitingVerifyProof[votedPointer] == 0)votedPointer ++;
    }

    function voteProofByPointer(uint32 curPointer, bool validProof)
        public
        ownerExists(msg.sender)
        validVoteByPointer(msg.sender, curPointer)
    {
        //update counts
        if(validProof) {
            validCount[curPointer] ++;
        }
        votedCount[curPointer] ++;

        //judge if there is enough owners voted
        if (votedCount[curPointer] == requiredOwnerCount) {
            if (validCount[curPointer] >= requiredValidVotesCount) {
                verifiedMerkleProof[waitingVerifyProof[curPointer]] = true;
            } else {
                delete MerkleProofTree[waitingVerifyProof[curPointer]];
            }
            delete waitingVerifyProof[curPointer];
            delete validCount[curPointer];
            delete votedCount[curPointer];
        }

        //update the pointer
        while(votedPointer < waitingVerifyProof.length &&
            waitingVerifyProof[votedPointer] == 0)votedPointer ++;
    }

    function getMerkleProofByHash(bytes32 keccakhash)
        public
        view
        ownerExists(msg.sender)
        returns (string memory a, bytes32 s, bytes32 k, bytes32 v)
    {
        MerkleProof storage toGet = MerkleProofTree[keccakhash];
        a = toGet.blockaddr;
        s = toGet.storagehash;
        k = toGet.key;
        v = toGet.value;
    }

    function getMerkleProofByPointer(uint32 curPointer)
        public
        view
        ownerExists(msg.sender)
        returns (string memory a, bytes32 s, bytes32 k, bytes32 v)
    {
        MerkleProof storage toGet = MerkleProofTree[waitingVerifyProof[curPointer]];
        a = toGet.blockaddr;
        s = toGet.storagehash;
        k = toGet.key;
        v = toGet.value;
    }

    function getTobeVotes()
        public
        view
        ownerExists(msg.sender)
        returns (uint32)
    {
        return votedPointer;
    }

    function validMerkleProoforNot(bytes32 keccakhash)
         external
        view
        returns (bool)
    {
        return verifiedMerkleProof[keccakhash];
    }

    function getVaildMerkleProof(bytes32 keccakhash)
        public
        view
        returns (string memory a, bytes32 s, bytes32 k, bytes32 v)
    {
        require(verifiedMerkleProof[keccakhash] == true, "invalid");
        MerkleProof storage toGet = MerkleProofTree[keccakhash];
        a = toGet.blockaddr;
        s = toGet.storagehash;
        k = toGet.key;
        v = toGet.value;
    }

    /**********************************************************************
     *                       Action Storage System                        *
     **********************************************************************/

    function addAction(bytes32 msghash, bytes memory signature)
        // future will be private
        public
        ownerExists(msg.sender)
        returns (bytes32 keccakhash)
    {
        // require(pa != 0, "invalid pa address");
        // require(pz != 0, "invalid pz address");

        Action memory toAdd = Action(msghash, signature);
        keccakhash = keccak256(abi.encodePacked(msghash, signature));

        ActionTree[keccakhash]= toAdd;
    }

    function getAction(bytes32 keccakhash)
        public
        view
        returns (bytes32 msghash, bytes memory signature)
    {
        Action storage toGet = ActionTree[keccakhash];
        // pa = toGet.pa;
        // pz = toGet.pz;
		msghash = toGet.msghash;
        signature = toGet.signature;
    }

    /**********************************************************************
     *                         Transaction System                         *
     **********************************************************************/
	
	function txtest(address isc)
	    public
	    view
	    returns (uint len)
	{
	    return txsReference[isc].txInfo[0].actionHash.length;
	}
	
//	InsuranceSmartContractInterface isc;
	
	function addTransactionProposal(address isc_addr)
    	public
    	returns (bool addingSuccess)
	{
	    InsuranceSmartContractInterface isc = InsuranceSmartContractInterface(isc_addr);
		require(isc.isRawSender(msg.sender), "you have no access to upload ISC to NSB");
		// addingSuccess = false;
		txsStack.length++;
		Transactions storage txs = txsStack[txsStack.length - 1];
// 		txs.txInfo.length = isc.txInfoLength();
		txs.contract_addr = isc_addr;
		txsReference[isc_addr] = txsStack[txsStack.length - 1];
		// for(uint idx=0; idx < txs.txInfo.length; idx++)
		// {
		//     txs.txInfo[idx].txhash = isc.getTxInfoHash(idx);
		// }
		
		activeISC[isc_addr] = true;
		addingSuccess = true;
	}
	
	function addMerkleProofProposal(
		address isc_addr,
		uint txindex,
		string memory blockaddr,
		bytes32 storagehash,
		bytes32 key,
		bytes32 val
	)
    	public
    	returns (bytes32 keccakhash)
	{
	    InsuranceSmartContractInterface isc = InsuranceSmartContractInterface(isc_addr);
		require(isc.isTransactionOwner(msg.sender, txindex), "you have no access to update the merkle proof");
	    addMerkleProof(blockaddr, storagehash, key, val);
		proofHashCallback[keccakhash] = isc_addr;
		keccakhash = keccak256(abi.encodePacked(blockaddr, storagehash, key, val));
	}
	
	function addActionProposal(
		address isc_addr,
		uint txindex,
		uint actionindex,
		bytes32 msghash,
		bytes memory signature
	)
    	public
    	returns (bytes32 keccakhash)
	{
		// InsuranceSmartContractInterface isc = InsuranceSmartContractInterface(isc_addr);
		// assert isc.isTransactionOwner(msg.sender, txindex, actionindex)
		// assert actionindex < actionHash.length
	    Transactions storage txs = txsReference[isc_addr];
		if (actionindex >= txs.txInfo[txindex].actionHash.length) {
		    txs.txInfo[txindex].actionHash.length = actionindex + 1;
		}
		keccakhash = txs.txInfo[txindex].actionHash[actionindex] = addAction(msghash, signature);
	}
	
	function closeTransaction(address isc_addr)
    	public
    	returns (bool closeSuccess)
	{
	    InsuranceSmartContractInterface isc = InsuranceSmartContractInterface(isc_addr);
		closeSuccess = false;
		require(isc.closed(), "ISC is active now");
		activeISC[isc_addr] = false;
		closeSuccess = true;
	}
}