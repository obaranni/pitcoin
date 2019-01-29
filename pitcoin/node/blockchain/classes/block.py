from merkle import calculate_merkle_root as calc_merkle_root
import hashlib
from binascii import unhexlify
from transaction import CoinbaseTransaction
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))
from wallet import wifKeyToPrivateKey, fullSettlementPublicAddress, readKeyFromFile, signMessage
from serializer import Serializer
MINER_PRIV_WIF_FILE = os.path.join(os.path.dirname(__file__),  '..', 'storage', 'minerkey')

class Block:
    def __init__(self, timestamp, previous_hash,
                 transactions, block_id, nonce=0, block_hash=None):
        if transactions is None:
            transactions = []
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.set_coinbase_transaction(MINER_PRIV_WIF_FILE)
        self.nonce = nonce
        self.block_id = block_id
        self.merkle_root = None
        self.hash = block_hash

    def calculate_merkle_root(self):
        self.merkle_root = calc_merkle_root(self.transactions[:])

    def calculate_hash(self):
        block_data = bytes(str(self.timestamp) + self.previous_hash + str(self.nonce) + str(self.merkle_root), 'utf-8')
        self.hash = hashlib.sha256(block_data).hexdigest()

    def set_coinbase_transaction(self, miner_wif_priv_file):
        miner_priv_wif = readKeyFromFile(miner_wif_priv_file)
        miner_priv = wifKeyToPrivateKey(miner_priv_wif)
        miner_address = fullSettlementPublicAddress(miner_priv)
        coinbase_tx = CoinbaseTransaction(miner_address)
        coinbase_tx.calculate_hash()
        signature, verify_key = signMessage(miner_priv, coinbase_tx.get_hash())
        coinbase_tx.set_sign(signature, verify_key)
        serializer = Serializer(coinbase_tx)
        self.transactions.append(serializer.get_serialized_tx())

    def validate_transactions(self): # validates all transactions
        pass



"""
from pending_pool import TxPool

pool = TxPool()
txs = pool.get_last_txs(3)


import datetime

currentDT = datetime.datetime.now()
# print (str(currentDT), currentDT.timestamp(), int(currentDT.timestamp()))
new_block = Block(int(currentDT.timestamp()), 0, txs)
new_block.calculate_merkle_root() 
"""