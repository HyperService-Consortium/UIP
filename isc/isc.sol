pragma solidity ^0.4.22;
contract InsuranceSmartContract {
    uint constant public MAX_OWNER_COUNT = 50;
    uint constant public MAX_VALUE_PROPOSAL_COUNT = 5;
    
            //   0        1     2       3     4       5
    enum State { unknown, init, inited, open, opened, closed }
    
    struct TransactionState {
        State state;
        bytes32 thash;
        uint256 topen;
        uint256 tclose;
    }
    
    struct dest {
        address addr;
        uint256 amount;
    }
    
    //maybe private later
    mapping(address => uint256) public ownerfunds;
    mapping(bytes32 => dest[6] ) public reverseBlames;
    
    mapping (address => bool) public isowner;
    
    uint256 public remainingFund;
    
    modifier onlyOwner()
    {
        require(isowner[msg.sender], "owner doesn't exist.");
        _;
    }
    
    modifier validConstructorInput(uint256 translen, uint256 addrlen, uint256 amnlen)
    {
        uint256 mul6 = translen * 6;
        require(mul6 == addrlen, "no enough to-blame address list input");
        require(mul6 == amnlen, "no enough to-blame address list input");
        _;
    }
    
    constructor (address[] owners,uint[] funds,
        bytes32[] transaction_id, address[] dest_addr, uint256[] dest_amount)
    public
    validConstructorInput(transaction_id.length, dest_addr.length, dest_amount.length)
    {
        for(uint idx = 0; idx < owners.length; idx++)
        {
            require(!isowner[owners[idx]] && owners[idx] != 0, "owner exists or its address is invalid");
            ownerfunds[owners[idx]] = funds[idx];
        }
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