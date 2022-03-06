# pip install web3==5.0.0 for BSC
from web3 import Web3
import json
import pandas as pd
import time
import os
from dotenv import load_dotenv
load_dotenv('.env')

# Config
initialMintAmount = 300

# Connect
BSC_MAIN_NET = 'https://bsc-dataseed.binance.org/'
BSC_TEST_NET = 'https://data-seed-prebsc-1-s1.binance.org:8545/'
LOCAL_HOST = 'http://127.0.0.1:8545' # Ganache-cli
web3 = Web3(Web3.HTTPProvider(BSC_TEST_NET))

# Init Contract
with open('PATH/TO/CONTRACT.JSON', 'r') as file:
    data = file.read()

# Contract
abi = json.loads(data)
address = "CONTRACT_ADDRESS_HERE"
contract = web3.eth.contract(address=address, abi=abi["abi"])

# Network Vars
public = os.environ['PUBLIC']
privateKey = os.environ['PRIVATE']
chainId = web3.eth.chainId
starting_balance = web3.eth.getBalance(public)/10**18 # 10.592438129227165

# Contract Vars
fee = contract.functions.fee().call()
paused = contract.functions.paused().call()
nfts = contract.functions.getnfts().call()
owner = contract.functions.owner().call()
print('Is paused? ', paused)
print('Chain Id: ', chainId)
print('Starting fee: ', fee)
print('Starting Balance: ', starting_balance)
gas_used = []



def send_transaction(tx):
    signtx = web3.eth.account.sign_transaction(tx, private_key=privateKey)
    try:
        hash = web3.eth.sendRawTransaction(signtx.rawTransaction)
        gas = web3.eth.getTransaction(hash).gas
        gas_used.append(gas)
    except Exception as e:
        print(e)

# Check Paused Status
if paused:
    nonce = web3.eth.getTransactionCount(public)
    tx = contract.functions.setPaused().buildTransaction({'from': public, 'nonce': nonce, 'chainId': chainId})
    send_transaction(tx)

if fee > 0:
    # Change Fee  
    print('Changing Fee')  
    nonce = web3.eth.getTransactionCount(public)
    tx = contract.functions.setFee(0).buildTransaction({'from': public, 'nonce': nonce, 'chainId': chainId})
    send_transaction(tx)
    time.sleep(5)
    fee = contract.functions.fee().call()
    print('New fee: ', fee)

# Mint a initial nfts
while len(nfts) < initialMintAmount and fee == 0:
    print('Minting Panda: ', len(nfts))
    nonce = web3.eth.getTransactionCount(public)
    tx = contract.functions.mintPanda().buildTransaction({
                                            'from':public, 
                                            'nonce':nonce, 
                                            'chainId': chainId})
    send_transaction(tx)
    time.sleep(5)

    nfts = contract.functions.getnfts().call()


if fee == 0 and len(nfts) >= initialMintAmount:
    # Change fee back
    print('Changing fee back')
    nonce = web3.eth.getTransactionCount(public)
    tx = contract.functions.setFee(10**17).buildTransaction({'from': public, 'nonce': nonce, 'chainId': chainId})
    send_transaction(tx)
    fee = contract.functions.fee().call()
    print('New fee: ', fee)

# Gas Used
ending_balance = web3.eth.getBalance(public) /10**18
print()
print('Starting Balance: ', starting_balance)
print('Ending Balance: ', ending_balance)
print('Gas used in Eth: ', sum(gas_used)/10**9)
print('Total Spent in BNB: ', ((starting_balance - ending_balance)))
print()

# Count rarities by percentage
df = pd.DataFrame(nfts)
print('Nfts Amount: ', len(nfts))
print('Rarities divided by nfts: ')
print((df[1].value_counts()) / len(df))