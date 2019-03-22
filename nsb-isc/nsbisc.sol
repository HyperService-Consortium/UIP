pragma solidity ^0.4.22;
pragma solidity ^0.4.22;
contract NetworkStatusBlockChain {
    uint constant public MAX_OWNER_COUNT = 50;
    uint constant public MAX_VALUE_PROPOSAL_COUNT = 5;

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
        string signature;
    }

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

    // ActionTree (keccak256(Action) => Action)
    mapping (bytes32 => Action) public ActionTree; // slot 8

    // The Net State BlockChain(NSB) contract is owned by multple entities to ensure security.
    mapping (address => bool) public isOwner; // slot 9
    address[] public owners; // slot 10

    uint public requiredOwnerCount; // slot 11
        uint public requiredValidVotesCount; // slot 12

    // Maps used for adding and removing owners.
    mapping (address => mapping (address => bool)) public addingOwnerProposal; // slot 13
    mapping (address => mapping (address => bool)) public removingOwnerProposal; // slot 14


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
     *                         Owner System End                           *
     **********************************************************************/

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
     *                  MerkleProof Storage System End                    *
     **********************************************************************/

    /**********************************************************************
     *                       Action Storage System                        *
     **********************************************************************/

    function addAction(string signature)
        public
        ownerExists(msg.sender)
        returns (bytes32 keccakhash)
    {
        // require(pa != 0, "invalid pa address");
        // require(pz != 0, "invalid pz address");

        Action memory toAdd = Action(signature);
        keccakhash = keccak256(signature);

        ActionTree[keccakhash]= toAdd;
    }

    function getAction(bytes32 keccakhash)
        public
        view
        returns (string signature)
    {
        Action storage toGet = ActionTree[keccakhash];
        // pa = toGet.pa;
        // pz = toGet.pz;
        signature = toGet.signature;
    }

    /**********************************************************************
     *                    Action Storage System End                       *
     **********************************************************************/

}


contract InsuranceSmartContract {
    uint constant public MAX_OWNER_COUNT = 50;
    uint constant public MAX_VALUE_PROPOSAL_COUNT = 5;

            //   0        1     2       3     4       5
    enum State { unknown, init, inited, open, opened, closed }

    struct TransactionState {
        State state;
        uint256 topen;
        uint256 tclose;
        mapping(string => string) result;
        string[] field;
    }

    struct Transaction {
        address fr;
        address to;
        uint seq;
        mapping(string => string) meta;
        string[] field;
    }

    //maybe private later
    mapping (address => uint256) public ownerfunds;

    mapping (address => bool) public isowner;

    uint256 public remainingFund;

    Transaction[] public txInfo;

    TransactionState[] public txState;


    modifier onlyOwner()
    {
        require(isowner[msg.sender], "owner doesn't exist.");
        _;
    }

    constructor (address[] owners,uint[] funds,
        bytes32[] transaction_content)
    public
    {
        uint idx;
        uint idy;
        uint bse;
        uint meta_length;
        txInfo.length++;
        Transaction storage to_Add = txInfo[0];
        txState.length++;
        for(idx = 0; idx < owners.length; idx++)
        {
            require(!isowner[owners[idx]] && owners[idx] != 0, "owner exists or its address is invalid");
            ownerfunds[owners[idx]] = funds[idx];
        }
        for(idx = 0; ; )
        {
            bse = idx + 4;
            require(bse <= transaction_content.length, "invalid transaction base info");
            to_Add.fr = bytes32ToAddress(transaction_content[idx]);
            to_Add.to = bytes32ToAddress(transaction_content[idx + 1]);
            to_Add.seq = uint(transaction_content[idx + 2]);
            meta_length = uint(transaction_content[idx + 3]);
            to_Add.field.length = meta_length;
            meta_length <<= 1;
            require(bse + meta_length <= transaction_content.length, "invalid transaction meta_length");
            for(idy = 0; idy < meta_length; idy += 2)
            {
                to_Add.field[idx >> 1] = bytes32ToString(transaction_content[bse + idy]);
                to_Add.meta[to_Add.field[idx >> 1]] = bytes32ToString(transaction_content[bse + idy + 1]);
            }
            idx = bse + meta_length;
            if(idx == transaction_content.length) break;
            txInfo.length++;
            txState.length++;
            to_Add = txInfo[txInfo.length - 1];
            //test.push(bytes32ToString(transaction_content[idy]));
        }
    }

    string aaf;
    function test(NetworkStatusBlockChain nsb, address cross) public view returns(bool){
        return nsb.isOwner(cross);
    }

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

    function getMetaByNumber(uint idx, uint idy)
    public
    view
    returns (string)
    {
        require(idx < txInfo.length, "idx overflow");
        require(idy < txInfo[idx].field.length, "idy overflow");
        return txInfo[idx].meta[txInfo[idx].field[idy]];
    }

    function getState(uint idx)
    public
    view
    returns (State)
    {
        require(idx < txInfo.length, "idx overflow");
        return txState[idx].state;
    }

    function stakeFund()
        public
        payable
        onlyOwner
    {
        remainingFund = safeAdd(remainingFund, msg.value);
    }

    function safeMul(uint256 a, uint256 b)
        internal
        pure
        returns (uint256 )
    {
        uint256 c = a * b;
        assert(a == 0 || c / a == b);
        return c;
    }

    function safeDiv(uint256 a, uint256 b)
        internal
        pure
        returns (uint256 )
    {
        assert(b > 0);
        uint256 c = a / b;
        assert(a == b * c + a % b);
        return c;
    }

    function safeSub(uint256 a, uint256 b)
        internal
        pure
        returns (uint256 )
    {
        assert(b <= a);
        return a - b;
    }

    function safeAdd(uint256 a, uint256 b)
        internal
        pure
        returns (uint256 )
    {
        uint256 c = a + b;
        assert(c >= a);
        return c;
    }
}
