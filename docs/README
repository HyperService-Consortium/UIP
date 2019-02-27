# A Summary of UIP(Universal Inter-blockchain Protocol)

## Introduction

**Blockchain interoperability**, that is, allowing state transitions across different blockchain networks, would facilitate more significant blockchain adoption. However, existing protocols are neither general enough to natively interconnect arbitrary blockchain networks, nor secure enough to prove the correctness of inter-chain operations, causing today's blockchain networks to be **isolated islands**.

In this paper, we present UIP(Universal Inter-Blockchain Protocol), the first **generic**, **secure**, and **trustfree** inter-chain protocol that enables true blockchain interoperability.

UIP is:

**generic** operating on any blockchain with a public transaction ledger.

**secure** each inter-chain operation either finishes with verifiable correctness or aborts due to security violations.

**financially safe** applications of UIP can be made **financially atomic**, regardless
of how or where the applications terminate.

------

## Major challenges

We recognize at least three major challenges in this regard.

First, the interoperability protocol should be **universally applicable**, such that it facilitates interoperation among various types of underlying blockchain networks.

Second, a blockchain network is generally abstracted as a **persistent state machine** whose correctness is ensured by its consensus protocol. However, it is difficult to ensure the correctness of multichain state transitions since executions on different blockchains are **not synchronized**.

Third, blockchain is touted as a technology for revolutionizing the financial sector, which usually demands stricter security requirements, including **financial safety**, **transaction integrity**, and **accountability**.

To further evaluate UIP's functionality, we build a [prototype platform][prototype platform] containing four independent blockchain networks with distinct consensus protocols, upon which we implement two categories of decentralized applications using UIP. Through our experiments, we demonstrate the **feasibility** of UIP in practice and show that these UIP-powered applications advance the state-of-the-art blockchain applications.

------

## List of notations

- inter-BN operation $(\mathcal {A},out)=\mathrm{Op}(\mathcal{G_T},\mathsf{ISC},\mathsf{VES})$.
- transaction set as a dependency graph $\mathcal{G_T}$.
- the collection of security attestations $\mathcal A$. 
- transaction $\mathcal{T}:=[\left<\text{from }\mathsf{fr},\text{to }\mathsf{to}\right>,\text{seq }\mathsf{Seq},\text{meta } \mathcal{M}]$ corresponding on-chain transaction $\widetilde{ \mathcal{T}}$.
- address pair $\left<\mathsf{fr},\mathsf{to}\right>$ decides the sending and receiving addresses.
- $\mathsf{Seq}$ is the sequence number of $\mathcal{T}$.
- meta $\mathcal {M}=[\text{amt }\mathsf{amt},\dots]$ structured and customizable metadata associated with $\mathcal{T}$.

------

## Component

In this article, we present UIP that simultaneously offer generic, secure and financially safe inter-blockchain. To ensure these properties, UIP consists of three novel components that work seamlessly together:VES, NSB, and ISC.

### Verifiable Execution System(VES)

- a trust-free service.
- a distributed system.
- takes cross-chain operations given by the dApp, and decomposes them into a transaction dependency graph $\mathcal{G}$ executes transaction across several blockchains on behalf of a decentralized application(dApp).
- drives the cross-BN executions.

### Network Status Blockchain(NSB)

- a blockchain of blockchains.
- a crucial security extension to UIP
- to enforce the operation correctness in a trust free manner.
- to provide an objective view on the operation status guaranteed by **Merkle proof**.
- consolidates a unified point-of-view of each underlying BNs' transactions and transaction pools.
- to prove the status of each transaction in the $\mathcal G$ and their actions taken while executing the $\mathcal  {G}$.
- providing an objective and trust-free environment for monitoring the transaction status for $\text{Op}$.
- enables **Proofs of Actions (PoAs)** for both the dApp and VES.
- ensuring that the ISC has sufficient information to decide which party to blame if $\text{Op}$ aborts incorrectly.

### Insurance Smart Contact(ISC)

- to enforce the operation correctness in a trust free manner.
- takes the Merkle proofs reported by both parts(dApp and VES).

## Architecture

### Decentralized Application(dApp)

- Clients of UIP.

### Blockchain networks(BNs)

### Correctness model(Transaction Dependency Graph $\mathcal{G_T}$).

- Specifies the **preconditions(2,3) and deadlines(4,5,6)** on these transactions.
- 2.the transaction intent can  proceed only if all its dependent intents are finalized.
- 3.imposing preconditions on cross-BN executions enables UIP to **navigate** a dApp from its source state to its destination state via dApp-defined "routing", even though transactions executed on different BNs are **not synchronized**.
- 4.achieve timely cross-BN executions.
- 5.ensure forward progress.
- 6.preventing malicious entity from taking an arbitrary amount of time to perform the next step of $\text {OP}$.

### Relationship

UIP overall Architecture:

$\text{dApps}\xrightarrow{\text{Op-intent}}\text{VESes}\xrightarrow{\text{Reachability}}\text{BNs}$.

Cross-Chain Execution:

$\text{dApp}\overset{\text{state}}{\longleftrightarrow}\text{VES},\text{dApp,VES}\overset{\text{Action}}{\longrightarrow}\text{NSB},\text{NSB}\overset{\text{PoA}}{\longrightarrow}\text{dApp,VES}$

## Protocol overview

### Session Setup for $\text{Op}$

- computing the transaction dependency graph $\mathcal {G_T}$.
- deploying the insurance contract ISC.
- Linkability between transaction intent in $\mathcal {G_T}$ with their corresponding on-chain counterparts is a prerequisite for the ISC to insure the execution of $\mathcal {G_T}$.
- $\left<\mathsf{fr},\mathsf{to}\right>$ pair in $\mathcal{T}$ must be consistent with the pair specified in $\mathcal{T}$ 's corresponding on-chain transaction $\widetilde{T}$.
- Both parties should mutually agree on $\mathcal{G_{T}}$ before proceeding to the execution phase of $\text{Op}$.

correctness: 

- commitment of all transactions.
- meta of each transaction intent is correctly populated with proper $\mathsf{amt}$， linkability capability,and some customized configuration if specified.
- rely on a customizable field in meta(**not** must be $\mathsf{amt}$) for linkability as long as programmatically recognizable by ISC.

### Cross-BN Execution for $\text{Op}$

First we define status{unknown, open, closed}. initialized as unknown.

The status of a transaction intent $\mathcal T $ becomes eligible for opening if each precondition of $\mathcal T$ has been **finalized** with correct **proof**. And it becomes closed at a predefined stage in $\widetilde{T}$'s lifecycle.

Three stage of each transaction intent $\mathcal T$:

1. **Open stage** $\mathcal D$ and $\mathcal V$ compute an open attestation to prove $\mathcal T  $ is eligible to be opened and after finishing successfully both parties proceed with it.
2. **Dispatch stage** the originator of $\mathcal T$ computes the $\widetilde {T}$ and post it on its destination BN for on-chain execution.
3. **Close stage** $\mathcal D$ and $\mathcal V$ compute an closed attestation to prove $\mathcal T  $ has finished executing. 

### ISC Initialization and Configuration

In the initialization step, the ISC should:

- instantiated with proper configuration
- installed with arbitration logic for deciding the final status of $\text{Op}$.

the ISC is based on the statuses enclosed in all received attentions, and identifies the accountable entities using a decision tree built based on the PoAs submitted by $\mathcal D$ and $\mathcal V $.

### Block Format

block header$\text{\{Prevhash，BlockNumber，Hash，StatusRoot，ActionRoot，OtherRoots}\}$

PrevHash: the Hash-pointer to the previous block.

BlockNumber: the unique index number of the block.

Hash: the number in hex maps from the total block header.

StatusRoot: the root of a lexicographically sorted Merkle tree whose leaves store the transaction status of underlying BNs, which consists of three lists: Tx Roots, State Roots, and Tx Claims.

ActionRoot: the root of a sorted Merkle tree whose leaf nodes store certificates computed by both parties. 

[prototype platform]: https://sites.google.com/view/universal-inter-bn-protocol/platform


