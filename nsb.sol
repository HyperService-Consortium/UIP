pragma solidity ^0.5.0;

interface InsuranceSmartContractInterface {
    
    function isRawSender(address) external view returns(bool);
    
    function txInfoLength() external view returns(uint);
    
    function getTxInfoHash(uint) external view returns(bytes32);
    
    function isTransactionOwner(address, uint) external view returns(bool);
    
    function closed()  external view returns(bool);
}

interface NetworkStatusBlockChainInterface {
    function validMerkleProoforNot(bytes32) external view returns(bool);
}

contract NetworkStatusBlockChain is NetworkStatusBlockChainInterface {
    ...
	
	function addTransactionProposal(address isc_addr)
    	public
    	returns (bool addingSuccess)
	{
	    InsuranceSmartContractInterface isc = InsuranceSmartContractInterface(isc_addr);
        /**  Wrong here
		require(isc.isRawSender(msg.sender), "you have no access to upload ISC to NSB");
		**/
        
        // addingSuccess = false;
		txsStack.length++;
		Transactions storage txs = txsStack[txsStack.length - 1];
 		/**  Wrong here
		txs.txInfo.length = isc.txInfoLength();
		**/
        txs.contract_addr = isc_addr;
		txsReference[isc_addr] = txsStack[txsStack.length - 1];
        /**  Wrong here
		for(uint idx=0; idx < txs.txInfo.length; idx++)
		{
		    txs.txInfo[idx].txhash = isc.getTxInfoHash(idx);
		}
		**/
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