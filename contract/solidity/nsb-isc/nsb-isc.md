# NSB (Network Status Blockchain)

The work of NSB is to verify the validity of the transaction.

## Owner System

Owner System use the invitation mechanism.

### `addOwner`

### `removeOwner`

### `checkOwner`

### `getOwner`

## Merkle Proof Storage System

Merkle Proof Storage System is responsible for managing Merkle Proofs from VES/dApp.

### `addMerkleProof`

### `voteMerkleProof`

### `getMerkleProof`

### `checkMerkleProof`

### `Struct MerkleProof`

##### `Attribute blockid`

##### `Attribute storagehash`

##### `Attribute key`

##### `Attribute value`

## Action Storage System

Action Storage System is responsible for managing Actions from VES/dApp.

### `addAction`

### `getAction`

### `Struct Action`

##### `Attribute msghash`

##### `Attribute signature`

## Transaction System

Based on the Merkle Proof Storage System and Action Storage System, Transaction System provides methods of complete cross-chain transaction management.

### `addTransactionProposal`

### `addTransactionInfo`

### `addTransactionFinish`

### `addMerkleProofProposal`

### `addActionProposal`

### `validateOutput`

### `validateAction`

### `CloseTransaction`

### `getTransactionInfo`

### slot(0)  `bytes32[] public waitingVerifyProof`

### slot(1)  `uint32[] public validCount`

### slot(2)  `uint32[] public votedCount`

### slot(3)  `mapping (bytes32 => uint32) public proofPointer`

### slot(4)  `mapping (address => mapping (bytes32 => bool)) public ownerVoted`

### slot(5)  `uint32 public votedPointer`

### slot(6)  `mapping (bytes32 => MerkleProof) public MerkleProofTree`

### slot(7)  `mapping (bytes32 => bool) public verifiedMerkleProof`

### slot(8)  `mapping (bytes32 => Action) public ActionTree`

### slot(9)  `mapping (address => bool) public isOwner`

### slot(10)  `address[] public owners` 

### slot(11)  `uint public requiredOwnerCount`

### slot(12)  `uint public requiredValidVotesCount`

### slot(13)  `mapping (address => mapping (address => bool)) public addingOwnerProposal`

### slot(14)  `mapping (address => mapping (address => bool)) public removingOwnerProposal`

# ISC

负责专门的transaction

### `constrcutor`

### `updateTxInfo`

### `ISCTxInfoUpdateFinished`

### `openISC`

### `InsuranceClaim`

### `SettleContract`