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
        // message hash
        // bytes32 msghash;
        // signature
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
    
    struct CallbackPair {
        // callback isc
        address isc_addr;
        // callback tx_count
        uint tx_index;
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
    mapping (bytes => bool) public validActionorNot;

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
	mapping (bytes32 => CallbackPair) public proofHashCallback; // slot 18
    
    /**********************************************************************
     *                      event & condition                             *
     **********************************************************************/
    
    event addingMerkleProof(string, bytes32, bytes32, bytes32);
    event addISCSuccess(address, uint);
    

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
        //ownerExists(msg.sender)
        validMerkleProof(storagehash, key)
        returns (bytes32 keccakhash)
    {
        MerkleProof memory toAdd = MerkleProof(blockaddr, storagehash, key, val);
        keccakhash = keccak256(abi.encodePacked(blockaddr, storagehash, key, val));

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
                CallbackPair storage cb = proofHashCallback[keccakhash];
                if(cb.isc_addr != address(0)) {
                    txsReference[cb.isc_addr].txInfo[cb.tx_index].proofHash.push(keccakhash);
                }
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
                CallbackPair storage cb = proofHashCallback[waitingVerifyProof[curPointer]];
                if(cb.isc_addr != address(0)) {
                    txsReference[cb.isc_addr].txInfo[cb.tx_index].proofHash.push(waitingVerifyProof[curPointer]);
                }
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
        // require(verify(msg, signature))
        Action memory toAdd = Action(signature);
        keccakhash = keccak256(abi.encodePacked(signature));
        validActionorNot(signature) = true;
        ActionTree[keccakhash]= toAdd;
    }

    function getAction(bytes32 keccakhash)
        public
        view
        returns (bytes memory signature)
    {
        Action storage toGet = ActionTree[keccakhash];
        // pa = toGet.pa;
        // pz = toGet.pz;
		// msghash = toGet.msghash;
        signature = toGet.signature;
    }

    // state variable
    // function validActionorNot(bytes memory signature)
    //     public
    //     view
    //     returns (bool)
    // {
    //
    // }

    /**********************************************************************
     *                         Transaction System                         *
     **********************************************************************/
	
//	InsuranceSmartContract isc;
	
	function addTransactionProposal(address isc_addr, uint tx_count)
    	public
    	returns (bool addingSuccess)
	{
	    // InsuranceSmartContract isc = InsuranceSmartContract(isc_addr);
		// require(isc.isRawSender(msg.sender), "you have no access to upload ISC to NSB");
		// addingSuccess = false;
		txsStack.length++;
		Transactions storage txs = txsStack[txsStack.length - 1];
 		txs.txInfo.length = tx_count;
		txs.contract_addr = isc_addr;
		txsReference[isc_addr] = txsStack[txsStack.length - 1];
		// for(uint idx=0; idx < txs.txInfo.length; idx++)
		// {
		//     txs.txInfo[idx].txhash = isc.getTxInfoHash(idx);
		// }
		
		activeISC[isc_addr] = true;
		addingSuccess = true;
		emit addISCSuccess(isc_addr, tx_count);
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
	    require(activeISC[isc_addr], "this isc is not active now");
		require(txsReference[isc_addr].txInfo.length > txindex, "index overflow");
	    // InsuranceSmartContract isc = InsuranceSmartContract(isc_addr);
		// require(isc.isTransactionOwner(msg.sender, txindex), "you have no access to update the merkle proof");
	    keccakhash = addMerkleProof(blockaddr, storagehash, key, val);
		proofHashCallback[keccakhash] = CallbackPair(isc_addr, txindex);
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
	    require(activeISC[isc_addr], "this isc is not active now");
	    // InsuranceSmartContract isc = InsuranceSmartContract(isc_addr);
		// assert isc.isTransactionOwner(msg.sender, txindex, actionindex)
		// assert actionindex < actionHash.length
	    Transactions storage txs = txsReference[isc_addr];
		require(txs.txInfo.length > txindex, "index overflow");
		if (actionindex >= txs.txInfo[txindex].actionHash.length) {
		    txs.txInfo[txindex].actionHash.length = actionindex + 1;
		}
		keccakhash = txs.txInfo[txindex].actionHash[actionindex] = addAction(msghash, signature);
	}
	
	function closeTransaction(address isc_addr)
    	public
    	returns (bool closeSuccess)
	{
	    // InsuranceSmartContract isc = InsuranceSmartContract(isc_addr);
		closeSuccess = false;
		// require(isc.closed(), "ISC is active now");
		activeISC[isc_addr] = false;
		closeSuccess = true;
	}
}