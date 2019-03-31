pragma solidity ^0.4.22;


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
    ...
    
    function ChangeResult(address nsb_addr, uint tid, bytes32[] results)
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
    
    ...
    
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
    
    ...
}
