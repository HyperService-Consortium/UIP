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
    
    struct Transaction {
        address fr;
        address to;
        uint seq;
        string[] field;
        mapping(string => string) meta;
    }

    //maybe private later
    mapping(address => uint256) public ownerfunds;

    mapping (address => bool) public isowner;

    uint256 public remainingFund;

    Transaction[] public txInfo;

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
            to_Add = txInfo[txInfo.length - 1];
            //test.push(bytes32ToString(transaction_content[idy]));
        }
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