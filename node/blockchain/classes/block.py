from merkle import calculate_merkle_root as calc_merkle_root
import hashlib

class Block:
    def __init__(self, timestamp, previous_hash,
                 transactions, nonce=0):
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.set_coinbase_transaction()
        self.transactions = transactions
        self.nonce = nonce
        self.merkle_root = None
        self.hash = None

    def calculate_merkle_root(self):
        self.merkle_root = calc_merkle_root(self.transactions)

    def calculate_hash(self):
        self.hash = hashlib.sha256(self.timestamp + self.previous_hash +
                      self.transactions + self.nonce + self.merkle_root)

    def set_coinbase_transaction(self):
        pass

    def validate_transactions(self): # validates all transactions
        pass




from pending_pool import TxPool

pool = TxPool()
txs = pool.get_last_txs(3)


import datetime

currentDT = datetime.datetime.now()
# print (str(currentDT), currentDT.timestamp(), int(currentDT.timestamp()))
new_block = Block(int(currentDT.timestamp()), 0, txs)
new_block.calculate_merkle_root()