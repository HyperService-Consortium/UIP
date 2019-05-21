#include <eosiolib/eosio.hpp>
#include <string>

using namespace eosio;

class [[eosio::contract("AddressBook")]] AddressBook : public eosio::contract {

public:
    using contract::contract;
    
    // @abi table 
    struct MerkleProof {
        std::string path;
        
    }
}