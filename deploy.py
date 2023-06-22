from solcx import compile_standard, install_solc
import json
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

install_solc("0.8.19")

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.19",
)
with open("compiles_code.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

abi = json.loads(
    compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]

w3 = Web3(Web3.HTTPProvider("https://eth-goerli.g.alchemy.com/v2/kmkkpk4XPxv15ELMOHx3Oxqnpn9Dxyy9"))
chain_id = 5
my_address = "0x6c7253d1eB028aAB39753E1939e2CC068f650dCc"

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

nonce = w3.eth.getTransactionCount(my_address)
print((str)(nonce)+ " = nonce")

transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId":chain_id,
     "from": my_address,
     "nonce": nonce,
     "gasPrice": w3.eth.gas_price})
singed_txn = w3.eth.account.sign_transaction(transaction,private_key = os.getenv("PRIVATE_KEY"))
tx_hash = w3.eth.send_raw_transaction(singed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(simple_storage.functions.retrieve().call())

store_transaction = simple_storage.functions.store(15).buildTransaction(
    {"chainId":chain_id,
     "from": my_address,
     "nonce": nonce+1,
     "gasPrice": w3.eth.gas_price
     })
singed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key= os.getenv("PRIVATE_KEY"))
send_store_tx = w3.eth.send_raw_transaction(singed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

print(simple_storage.functions.retrieve().call())