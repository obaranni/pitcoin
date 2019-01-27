import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'blockchain', 'tools'))
from pending_pool import TxPool
from wallet import wifKeyToPrivateKey, fullSettlementPublicAddress, readKeyFromFile, signMessage
from serialized_txs_to_json import txs_to_json
from blocks_to_json import convert_blocks
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'classes'))
from block import Block
from transaction import CoinbaseTransaction
import datetime
import json


TRANSACTIONS_TO_MINE = 4
BASE_COMPLEXITY = 2
MAX_TX_TO_GET = 1000
BLOCKCHAIN_DB = os.path.join(os.path.dirname(__file__),  'storage', 'blocks')

class Blockchain:
    def __init__(self):
        self.blocks = []
        self.mine_mode = True # False
        self.load_chain()

    def change_mine_mode(self):
        self.mine_mode = not self.mine_mode

    def mine(self, block, complexity=BASE_COMPLEXITY):
        while block.hash[:complexity] != "0" * complexity:
            block.nonce += 1
            block.calculate_hash()
        return block

    def load_chain(self):
        # do i have other nodes?
        # do i have stored blocks?
        # no! you dont
        # okey, so lets begin from genesis
        if not self.mine_mode:
            return False
        block = self.mine(self.genesis_block())
        self.save_block(block)

    def resolve_conflicts(self):
        pass

    def is_valid_chain(self):
        pass

    def add_node(self):
        pass

    def save_blocks(self):
        file = open(BLOCKCHAIN_DB, 'w+')
        json_blocks = convert_blocks(self.blocks)
        json.dump(json_blocks, file, indent=4)
        file.close()

    def save_block(self, block):
        self.blocks.append(block)
        self.save_blocks()

    def create_block(self, txs):
        prev_hash = self.blocks[-1].hash
        block = Block(self.get_timestamp(), prev_hash, txs)
        block.calculate_merkle_root()
        block.calculate_hash()
        self.save_block(self.mine(block))

    def genesis_block(self):
        genesis_block = Block(self.get_timestamp(), "0" * 64, [])
        genesis_block.calculate_merkle_root()
        genesis_block.calculate_hash()
        return genesis_block

    def submit_tx(self, new_tx):
        tx_pool = TxPool()
        result = tx_pool.new_transaction(new_tx)
        if not result:
            return False
        pool_size = tx_pool.get_pool_size()
        if pool_size >= TRANSACTIONS_TO_MINE:
            print("Start mine. Txs in pool:", pool_size)
            print(tx_pool.get_last_txs(TRANSACTIONS_TO_MINE))
            self.create_block(tx_pool.get_last_txs(TRANSACTIONS_TO_MINE))
            tx_pool.delete_last_txs(TRANSACTIONS_TO_MINE)
        return result

    def get_pending_txs(self):
        return txs_to_json(TxPool().get_last_txs(MAX_TX_TO_GET))

    def get_timestamp(self):
        current_dt = datetime.datetime.now()
        return int(current_dt.timestamp())

    def 

