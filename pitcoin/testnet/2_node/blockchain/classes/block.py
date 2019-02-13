from merkle import calculate_merkle_root as calc_merkle_root
import hashlib
from binascii import unhexlify
from Transaction import CoinbaseTransaction
import sys, os, base58
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))
from wallet import wifKeyToPrivateKey, fullSettlementPublicAddress, readKeyFromFile, signMessage, getPublickKey, compressPublicKey, getAddresOfPublicKey

from serializer import Serializer
MINER_PRIV_WIF_FILE = os.path.join(os.path.dirname(__file__),  '..', 'storage', 'minerkey')

class Block:
    def __init__(self, timestamp, previous_hash,
                 transactions, block_id, reward, difficulty, nonce=0, block_hash=None, merkle_root=None):
        self.reward = reward
        self.difficulty = difficulty
        if transactions is None:
            transactions = []
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.transactions = transactions
        if block_hash is None:
            self.set_coinbase_transaction(MINER_PRIV_WIF_FILE)
        self.nonce = nonce
        self.block_id = block_id
        self.merkle_root = merkle_root
        self.hash = block_hash

    def calculate_merkle_root(self):
        self.merkle_root = calc_merkle_root(self.transactions[:])

    def calculate_hash(self):
        block_data = bytes(str(self.timestamp) + self.previous_hash + str(self.nonce) + str(self.merkle_root), 'utf-8')
        self.hash = hashlib.sha256(block_data).hexdigest()

    def set_coinbase_transaction(self, miner_wif_priv_file):
        miner_priv_wif = readKeyFromFile(miner_wif_priv_file)
        miner_priv = wifKeyToPrivateKey(miner_priv_wif)
        miner_address = fullSettlementPublicAddress("72c72f8bdccd8ec314cf85b68b09a2c0057cf476f6c1b56a7147b85693f586bb")
        tx = CoinbaseTransaction("{\"inputs\": [{\"tx_id\": \"" + "0" * 64 + "\", \"tx_out_id\": \"" + str(4294967295) + "\", \"tx_script\": \"\", \"value\": \"" + str(self.reward) + "\"}]}",
                "{\"outputs\": [{\"address\": \"" + miner_address + "\", \"value\": \"" + str(self.reward) + "\", \"script_type\": \"p2pkh\"}]}")
        tx.get_presign_raw_format()
        tx.calculate_hash()
        miner_pub = getPublickKey(miner_priv)
        sender_compressed_pub_key = compressPublicKey(miner_pub)
        tx.sign_tx(miner_priv)
        ser_tx = tx.get_signed_raw_format(sender_compressed_pub_key, is_coinbase=1).hex()
        self.transactions.append(ser_tx)

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