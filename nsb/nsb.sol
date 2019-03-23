pragma solidity ^0.4.22;
interface InsuranceSmartContract {
    
    function isRawSender(address) external returns(bool);
    
    function txInfoLength() external returns(uint);
    
    function getTxInfoHash(uint) external returns(bytes32);
    
    function isTransactionOwner(address, uint) external returns(bool);
    
    function closed() external returns(bool);
}

contract NetworkStatusBlockChain {
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
    
	Transactions[] private txsStack; // slot 15
	mapping (address => Transactions) txsReference; // slot 16
	mapping (address => bool) activeISC; // slot 17
	mapping (bytes32 => address) proofHashCallback; // slot 18
    
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
    constructor (address[] _owners, uint _required)
        public
        validRequirement(_owners.length, _required)
    {
        for (uint i = 0; i<_owners.length; i++) {
            require(!isOwner[_owners[i]] && _owners[i] != 0, "owner exists or its address is invalid");
            isOwner[_owners[i]] = true;
        }
        
        owners = _owners;
        requiredOwnerCount = _required;
        requiredValidVotesCount = (requiredOwnerCount + 1) >> 1;
    }

    /**********************************************************************
     *                            Owner System                            *
     **********************************************************************/

    function addOwner(address _newOwner)
        public
        ownerExists(msg.sender)
        validRequirement(owners.length + 1, requiredOwnerCount)
    {
        require(_newOwner != 0, "invalid owner address");
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
        returns (address[])
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
    function addMerkleProof(string blockaddr, bytes32 storagehash, bytes32 key, bytes32 val)
        public
        ownerExists(msg.sender)
        validMerkleProof(storagehash, key)
    {
        MerkleProof memory toAdd = MerkleProof(blockaddr, storagehash, key, val);
        bytes32 keccakhash = keccak256(blockaddr, storagehash, key, val);

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
        returns (string a, bytes32 s, bytes32 k, bytes32 v)
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
        returns (string a, bytes32 s, bytes32 k, bytes32 v)
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
        public
        view
        returns (bool)
    {
        return verifiedMerkleProof[keccakhash];
    }

    function getVaildMerkleProof(bytes32 keccakhash)
        public
        view
        returns (string a, bytes32 s, bytes32 k, bytes32 v)
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

    function addAction(bytes32 msghash, bytes signature)
        // future will be private
        public
        ownerExists(msg.sender)
        returns (bytes32 keccakhash)
    {
        // require(pa != 0, "invalid pa address");
        // require(pz != 0, "invalid pz address");

        Action memory toAdd = Action(msghash, signature);
        keccakhash = keccak256(msghash, signature);

        ActionTree[keccakhash]= toAdd;
    }

    function getAction(bytes32 keccakhash)
        public
        view
        returns (bytes32 msghash, bytes signature)
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
	
	function addTransactionProosal(InsuranceSmartContract isc)
    	public
    	returns (bool addingSuccess)
	{
		require(isc.isRawSender(msg.sender), "you have no access to upload ISC to NSB");
		// addingSuccess = false;
		txsStack.length++;
		Transactions storage txs = txsStack[txsStack.length - 1];
		txsReference[isc] = txs;
		txs.txInfo.length = isc.txInfoLength();
		for(uint idx=0; idx < txs.txInfo.length; idx++)
		{
		    txs.txInfo[idx].txhash = isc.getTxInfoHash(idx);
		}
		
		activeISC[isc] = true;
		addingSuccess = true;
	}
	
	function addMerkleProofProposal(
		InsuranceSmartContract isc,
		uint txindex,
		string blockaddr,
		bytes32 storagehash,
		bytes32 key,
		bytes32 val
	)
    	public
    	returns (bytes32 keccakhash)
	{
		require(isc.isTransactionOwner(msg.sender, txindex), "you have no access to update the merkle proof");
		addMerkleProof(blockaddr, storagehash, key, val);
		proofHashCallback[keccakhash] = isc;
		keccakhash = keccak256(blockaddr, storagehash, key, val);
	}
	
	function addActionProposal(
		InsuranceSmartContract isc,
		uint txindex,
		uint actionindex,
		bytes32 msghash,
		bytes signature
	)
    	public
    	returns (bytes32 keccakhash)
	{
		// assert isc.isTransactionOwner(msg.sender, txindex, actionindex)
		// assert actionindex < actionHash.length
		Transactions storage txs = txsReference[isc];
		keccakhash = txs.txInfo[txindex].actionHash[actionindex] = addAction(msghash, signature);
	}
	
	function closeTransaction(InsuranceSmartContract isc)
    	public
    	returns (bool closeSuccess)
	{
		closeSuccess = false;
		require(isc.closed(), "ISC is active now");
		activeISC[isc] = false;
		closeSuccess = true;
	}
}