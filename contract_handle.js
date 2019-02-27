// The file defines the ABI handle for interacting with HyperService contracts.
"use strict";


//web3.js
//let Web3 = require('ethereum/web3');
import Web3 from 'web3';

let FS = require("fs");

//geth's web3 HttpProvider
const web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
//console.log(web3);
//console.log(web3.eth.givenProvider);
//console.log(web3.eth.currentProvider);
/*const batch = new web3.BatchRequest();
batch.add(web3.eth.coinbase.request(//, 'latest',
	function(data){
		console.log(data);	
	}
));
*/

//var balanceWei = web3.eth.getBalance("0xC257274276a4E539741Ca11b590B9447B26A8051");
//console.log(balanceWei)
//batch.execute();
let ethAccounts = ["0x0"];
//web3.eth.getAccounts(console.log);
// web3.eth.getAccounts(
// 	function callback(unknownData, list){
// 		//console.log(unknowndata);
// 		console.log(ethAccounts);
// 		ethAccounts = list;
// 		//verifyAccounts();
// 	}
// );
// web3.eth.getBlock(1027, function(error, result){
// 	if(!error)
// 		console.log(JSON.stringify(result));
// 	else
// 		console.error(error);
//  })
//console.log(web3.eth.defaultBlock);
//console.log(web3.eth.defaultAccount);
//console.log(web3.eth.transactionBlockTimeout);

let broker_addr = "0xd7ea2b03da511799eb0c5a28989cf5268c869311";
let broker_abi = JSON.parse(FS.readFileSync('broker_abi', 'utf8'));

let hash = web3.sha3("Some string to be hashed");
console.log(hash);

//console.log(broker_abi);
//console.log(web3.eth.coinbase);
//console.log(web3.eth.accounts[0]);
//console.log(web3.admin);
let BrokerContract = {
	
	//create handle
    handle : new web3.eth.Contract(broker_abi,broker_addr),
    
	//sendTransaction?
    addOwner : function(cur_owner, new_owner) {
	this.handle.addOwner.sendTransaction(new_owner, {
	    from: cur_owner,
	    gas: 4000000
	}, function(error, result) {
	    if (error) {
		throw error;
	    }
	    console.log(result);
	    return result;
	});
    },

	//sendTransaction?
    removeOwner : function(addr) {
	this.handle.removeOwner.sendTransaction(addr, {
	    from: addr,
	    gas: 4000000
	}, function(error, result) {
	    if (error) {
		throw error;
	    }
	    return result;
	});
    },

	//addr:account's address
    setValueProposal : function(addr, value) {
	this.handle.setValueProposal.sendTransaction(value, {
	    from : addr,
	    gas: 4000000
	}, function(error, result) {
	    if (error) {
		throw error;
	    }
	    console.log(result);
	    return result;
	});
    },

    getGenuineValue : function(addr) {
	this.handle.getGenuineValue.sendTransaction({
	    from : addr,
	    gas : 4000000
	}, function(error, result) {
	    if (error) {
		throw error;
	    }
	    console.log(result);
	    return result;
	});
    },

    getGenuineValueLocalCall : function(addr) {
	this.handle.getGenuineValue.call({
	    from : addr,
	    gas : 4000000
	}, function(error, result) {
	    if (error) {
		throw error;
	    }
	    console.log(result);
	    return result;
	});
    },

};


let option_addr = "0xa0519c6050950b6c73bbd9d1605c4ffc867b518b";
let option_abi = JSON.parse(FS.readFileSync('option_abi', 'utf8'));

let OptionContract = {

    handle : new web3.eth.Contract(option_abi,option_addr),
    
    stakeFund : function(addr) {
	this.handle.stakeFund.sendTransaction({
	    from: addr,
	    gas: 4000000
	}, function(error, result) {
	    if (error) {
		throw error;
	    }
	    console.log(result);
	    return result;
	});
    },

    updateStake : function(addr, value) {
	this.handle.updateStake.sendTransaction(value, {
	    from: addr,
	    gas: 4000000
	}, function(error, result) {
	    if (error) {
		throw error;
	    }
	    console.log(result);
	    return result;
	});
    },

    buyOption : function(addr, value) {
	this.handle.buyOption.sendTransaction(value, {
	    from: addr,
	    gas: 4000000
	}, function(error, result) {
	    if (error) {
		throw error;
	    }
	    return result;
	});
    },

    cashSettle : function(addr, value) {
	this.handle.CashSettle.sendTransaction(value, {
	    from: addr,
	    gas: 4000000
	}, function(error, result) {
	    if (error) {
		throw error;
	    }
	    return result;
	});
    },

};

// Some examples for interacting with the contracts.
// Please refer to the contract definition in sol files for more details.
//web3.eth.coinbase(console.log);
// BrokerContract.addOwner(web3.eth.coinbase, web3.eth.accounts[1]);
// BrokerContract.setValueProposal(web3.eth.accounts[1], 200);
// BrokerContract.setValueProposal(web3.eth.coinbase, 100);
// BrokerContract.getGenuineValue(web3.eth.coinbase);

// OptionContract.stakeFund(web3.eth.coinbase);
// OptionContract.updateStake(web3.eth.coinbase, 700);
// OptionContract.buyOption(web3.eth.coinbase, 400);
// OptionContract.cashSettle(web3.eth.coinbase, 500);
