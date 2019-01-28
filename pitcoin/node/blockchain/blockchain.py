import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'blockchain', 'tools'))
from pending_pool import TxPool
from wallet import wifKeyToPrivateKey, fullSettlementPublicAddress, readKeyFromFile, signMessage
from serialized_txs_to_json import txs_to_json
from blocks_to_json import convert_blocks_to
from blocks_from_json import convert_blocks_from
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'classes'))
from block import Block
from transaction import CoinbaseTransaction
import datetime
import json


TRANSACTIONS_TO_MINE = 4
BASE_COMPLEXITY = 2
MAX_TX_TO_GET = 1000
BLOCKCHAIN_DB = os.path.join(os.path.dirname(__file__),  'storage', 'blocks')
NODE_FILE = os.path.join(os.path.dirname(__file__),  'storage', 'peers')


class Blockchain:
    def __init__(self):
        self.blocks = []
        self.mine_mode = False
        self.consensus_mode = False

    def change_mine_mode(self):
        self.mine_mode = not self.mine_mode
        if self.mine_mode:
            self.load_chain()
            self.start_mine()

    def mine(self, block, complexity=BASE_COMPLEXITY):
        while block.hash[:complexity] != "0" * complexity:
            block.nonce += 1
            block.calculate_hash()
        return block

    def start_mine(self):
        while True:
            txs = self.cut_transactions()
            if not txs:
                break
            self.create_block(txs[-TRANSACTIONS_TO_MINE:])

    def cut_transactions(self):
        tx_pool = TxPool()
        pool_size = tx_pool.get_pool_size()
        if pool_size < TRANSACTIONS_TO_MINE:
            return False
        print("Start mine. Txs in pool:", pool_size)
        txs = tx_pool.get_last_txs(MAX_TX_TO_GET)
        tx_pool.set_txs(txs[:TRANSACTIONS_TO_MINE])
        return txs

    def load_chain(self):
        # do i have other nodes?
        # do i have stored blocks?
        # no! you dont
        # okey, so lets begin from genesis
        if not self.mine_mode:
            return False
        txs = self.cut_transactions()
        if not txs:
            txs = None
        block = self.mine(self.genesis_block(txs))
        self.save_block(block)

    def change_consensus_mode(self):
        self.consensus_mode = not self.consensus_mode
        if self.consensus_mode:
            self.mine_mode = False

    def resolve_conflicts(self):
        pass

    def read_blocks(self):
        file = open(BLOCKCHAIN_DB)
        blocks = convert_blocks_from(file)
        file.close()
        return blocks

    def is_valid_chain(self):
        pass

    def save_blocks(self):
        file = open(BLOCKCHAIN_DB, 'w+')
        json_blocks = convert_blocks_to(self.blocks)
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

    def genesis_block(self, txs):
        genesis_block = Block(self.get_timestamp(), "0" * 64, txs)
        genesis_block.calculate_merkle_root()
        genesis_block.calculate_hash()
        return genesis_block

    def submit_tx(self, new_tx):
        tx_pool = TxPool()
        result = tx_pool.new_transaction(new_tx)
        if not result:
            return False
        if self.mine_mode:
            self.start_mine()
        return result

    def get_pending_txs(self):
        return txs_to_json(TxPool().get_last_txs(MAX_TX_TO_GET))

    def get_timestamp(self):
        current_dt = datetime.datetime.now()
        return int(current_dt.timestamp())

    def create_db_if_not_exist(self):
        file = open(BLOCKCHAIN_DB, 'a+')
        file.close()

    def get_full_blockchain(self):
        self.create_db_if_not_exist()
        result_line = ''
        file = open(BLOCKCHAIN_DB, 'r+')
        lines = file.readlines()
        for line in lines:
            result_line += line + '\n'
        file.close()
        print(result_line)
        return result_line

    def get_chain_length(self):
        return len(self.blocks)

    def add_node(self, ip):
        file = open(NODE_FILE, 'a+')
        print(ip)
        file.write("%s\n" % str(ip))
        file.close()
        return True
