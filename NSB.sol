pragma solidity ^0.4.22;
contract NetStateBlockChain {
    uint constant public MAX_OWNER_COUNT = 50;
    uint constant public MAX_VALUE_PROPOSAL_COUNT = 5;
    
    struct MerkleProof {
        //storage roothash
        bytes32 storagehash;
        //storaged key
        bytes32 key;
        // corresponding value
        bytes32 value;
    }
    // The actionTree
    // keccak256(storagehash + key + value) maps to MerkleProof
    bytes32[] public waitingVerifyProof;
    
    // corresponding valid votes' number
    uint32[] public validCount;
    
    // corresponding votes' number
    uint32[] public votedCount;
    
    // remained verifying MerkleProofs range [votedPointer, waitingVerifyProof.length)
    uint32 votedPointer;
    
    // all the actions on the contract
    mapping (bytes32 => MerkleProof) public actionTree;
    // if the action/proof Atte is valid, verifiedAction[Atte] == true
    mapping (bytes32 => bool) public verifiedAction;
    
    // The Net State BlockChain(NSB) contract is owned by multple entities to ensure security. 
    mapping (address => bool) public isOwner;
    address[] public owners;
    
    // remained caught MerkleProofs range [ownersPointer, waitingVerifyProof.length)
    mapping(address => uint32) public ownersPointer;
    // remained verifying MerkleProofs by onwers range [onwersvotedPointer, waitingVerifyProof.length)
    mapping(address => uint32) public ownersVotedPointer;
    uint public requiredOwnerCount;
    uint public requiredValidVotesCount;
    
    // Maps used for adding and removing owners. 
    mapping (address => mapping (address => bool)) public addingOwnerProposal;
    mapping (address => mapping (address => bool)) public removingOwnerProposal;
    
    modifier ownerDoesNotExist(address owner) {
        require(!isOwner[owner], "owner exists");
        _;
    }

    modifier ownerExists(address owner) {
        require(isOwner[owner], "onwer does not exist");
        _;
    }
    
    event addingMerkleProof(bytes32, bytes32, bytes32);
    
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
    
    modifier validVote(uint curVotedPointer) {
        require(votedPointer <= curVotedPointer, "the MerkleProof is proved");
        require(curVotedPointer <waitingVerifyProof.length, "no MerkleProof to vote");
        require(waitingVerifyProof[curVotedPointer] != 0, "the MerkleProof is proved");
        _;
    }
    
    modifier validUpdate(uint curPointer) {
        require(curPointer < votedPointer, "Remain Proof to verify");
        _;
    }
    
    modifier validChange(address addr, uint changeNum) {
        require(ownersVotedPointer[addr] <= changeNum, "too small");
        require(changeNum <waitingVerifyProof.length, "too big");
        _;
    }
    
    // Remember to specify at least one address and set the _required as one. 
    constructor (address[] _owners, uint _required) 
        public
        validRequirement(_owners.length, _required)
    {
        for (uint i = 0; i<_owners.length; i++) {
            require(!isOwner[_owners[i]] && _owners[i] != 0);
            isOwner[_owners[i]] = true;
        }
        owners = _owners;
        requiredOwnerCount = _required;
        requiredValidVotesCount = (requiredOwnerCount + 1) >> 1;
    }
    
    function addOwner(address _newOwner)
        public
        ownerExists(msg.sender)
        validRequirement(owners.length + 1, requiredOwnerCount)
    {
        require(_newOwner != 0);
        addingOwnerProposal[_newOwner][msg.sender] = true;
        
        //use a integer to count it?
        uint vote_count = 0;
        for (uint i = 0; i < owners.length; i++) {
            address owner = owners[i];
            if (addingOwnerProposal[_newOwner][owner] == true) {
                vote_count += 1;
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
                vote_count += 1;
            }
        }
        
        // Removing owner proposal is approved.
        if (vote_count >= requiredOwnerCount) {
            isOwner[_removeOwner] = false;
            for (uint j = 0; j < owners.length - 1; j++) {
                if (owners[i] == _removeOwner) {
                    owners[i] = owners[owners.length - 1];
                    break;
                }
            }
        }
        owners.length -= 1;
    }
    
    // change it to VES/DAPP/NSB user?
    function addMerkleProof(bytes32 storagehash, bytes32 key, bytes32 val)
        public
        ownerExists(msg.sender)
        validMerkleProof(storagehash, key)
    {
        MerkleProof memory toAdd = MerkleProof(storagehash, key, val);
        bytes32 keccakhash = keccak256(storagehash, key, val);
        waitingVerifyProof.push(keccakhash);
        actionTree[keccakhash] = toAdd;
        emit addingMerkleProof(storagehash, key, val);
    }
    
    function getMerkleProof()
        public
        remainMerkleProof(uint(ownersPointer[msg.sender]))
        returns (bytes32 s, bytes32 k, bytes32 v)
    {
        while(waitingVerifyProof[ownersPointer[msg.sender]] == 0) ownersPointer[msg.sender] += 1;
        MerkleProof storage toGet = actionTree[waitingVerifyProof[ownersPointer[msg.sender]]];
        ownersPointer[msg.sender] += 1;
        s = toGet.storagehash;
        k = toGet.key;
        v = toGet.value;
    }
    function voteProof(bool validProof)
        validVote(uint(ownersVotedPointer[msg.sender]))
        public
    {
        uint32 curPointer = ownersVotedPointer[msg.sender];
        ownersVotedPointer[msg.sender] += 1;
        if(validProof) {
            validCount[curPointer] += 1;
        }
        votedCount[curPointer] += 1;
        if (votedCount[curPointer] == requiredOwnerCount) {
            if (validCount[curPointer] >= requiredValidVotesCount) {
                verifiedAction[waitingVerifyProof[curPointer]] = true;
            } else {
                delete actionTree[waitingVerifyProof[curPointer]];
            }
            delete waitingVerifyProof[curPointer];
            delete validCount[curPointer];
            delete votedCount[curPointer];
        }
        ownersVotedPointer[msg.sender] += 1;
        while(waitingVerifyProof[votedPointer] == 0)votedPointer += 1;
    }
    function updateToLatestVote()
        public
        validUpdate(uint(ownersVotedPointer[msg.sender]))
    {
        ownersVotedPointer[msg.sender] = votedPointer;
        if(ownersPointer[msg.sender] < votedPointer) {
            ownersPointer[msg.sender] = votedPointer;
        }
    }
    
    function resetGetPointer(uint32 num)
        public
        validChange(msg.sender, num)
    {
        ownersPointer[msg.sender] = num;
    }
    
    //is it necessary?
    function reGetMerkleProof(bytes32 keccakhash)
        public
        view
        returns (bytes32 s, bytes32 k, bytes32 v)
    {
        // require(actionTree[keccakhash] != , "not exists");
        MerkleProof storage toGet = actionTree[keccakhash];
        s = toGet.storagehash;
        k = toGet.key;
        v = toGet.value;
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
    
    function getTobeVotes()
        public
        view
        returns (uint32)
    {
        return ownersVotedPointer[msg.sender];
    }
    
    function validMerkleProoforNot(bytes32 keccakhash)
        public
        view
        returns (bool)
    {
        return verifiedAction[keccakhash];
    }
    
    function getVaildMerkleProof(bytes32 keccakhash)
        public
        view
        returns (bytes32 s, bytes32 k, bytes32 v)
    {
        require(verifiedAction[keccakhash] == true, "invalid");
        MerkleProof storage toGet = actionTree[keccakhash];
        s = toGet.storagehash;
        k = toGet.key;
        v = toGet.value;
    }
}
