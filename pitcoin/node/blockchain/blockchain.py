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
from flask import request

TRANSACTIONS_TO_MINE = 4
BASE_COMPLEXITY = 2
MAX_TX_TO_GET = 1000
BLOCKCHAIN_DB = os.path.join(os.path.dirname(__file__),  'storage', 'blocks')
PEERS_FILE = os.path.join(os.path.dirname(__file__),  'storage', 'peers')


class Blockchain:
    def __init__(self):
        self.blocks = []
        self.mine_mode = False
        self.consensus_mode = False
        self.load_chain()

    def change_mine_mode(self):
        self.mine_mode = not self.mine_mode
        if self.mine_mode:
            print("[from: node]: Mining mode: on")
            self.start_mining()
        else:
            print("[from: node]: Mining mode: off")

    def mining_hash(self, block, complexity=BASE_COMPLEXITY):
        while block.hash[:complexity] != "0" * complexity:
            block.nonce += 1
            block.calculate_hash()
        return block

    def cut_transactions(self):
        tx_pool = TxPool()
        pool_size = tx_pool.get_pool_size()
        if pool_size < TRANSACTIONS_TO_MINE:
            return False
        print("[from: node]: Txs in pool: %d. Start mining" % pool_size)
        txs = tx_pool.get_last_txs(MAX_TX_TO_GET)
        tx_pool.set_txs(txs[TRANSACTIONS_TO_MINE:])
        return txs[:TRANSACTIONS_TO_MINE]

    def start_mining(self):
        flag = 0
        while True:
            txs = self.cut_transactions()
            if not txs:
                if flag:
                    break
                return False
            else:
                flag = 1
            self.create_block(txs[:TRANSACTIONS_TO_MINE])
        print("[from: node]: Mining is over. Current blockchain height:", self.get_chain_length())

    def create_chain(self):
        txs = self.cut_transactions()
        if not txs:
            txs = None
            print("[from: node]: Empty txs pool. Generate genesis block with one tx")
        block = self.mining_hash(self.genesis_block(txs))
        self.save_block(block)

    def load_block_from_db(self):
        self.create_db_if_not_exist()
        try:
            file = open(BLOCKCHAIN_DB, 'r')
            blocks_json = convert_blocks_from(file)
            file.close()
        except json.decoder.JSONDecodeError:
            return None
        return blocks_json

    def load_chain(self):
        print("[from: node]: Node started successfully")
        print("[from: node]: Consensus mode: off")
        print("[from: node]: Mining mode: off")
        blocks = self.load_block_from_db()
        if blocks is None:
            print("[from: node]: Database is empty")
        else:
            print("[from: node]: Loading blocks from database...")
            self.blocks = blocks
            print("[from: node]: Done")
            print("[from: node]: Chain height:", self.get_chain_length())
        print("[from: node]: transactions in pool:", TxPool().get_pool_size())

        # do i have other nodes?
        # do i have stored blocks?
        # no! you dont
        # okey, so lets begin from genesis
        if not self.mine_mode:
            return False
        if len(self.blocks) < 1:
            self.create_chain()


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
        self.save_block(self.mining_hash(block))

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
        pool_size = tx_pool.get_pool_size()
        print("[from: node]: New tx! Current pool size:", pool_size)
        if self.mine_mode:
            self.start_mining()
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
        file = open(BLOCKCHAIN_DB, 'r')
        lines = file.readlines()
        for line in lines:
            result_line += line + '\n'
        file.close()
        return result_line

    def get_chain_length(self):
        return len(self.blocks)

    def create_peers_if_not_exist(self):
        file = open(PEERS_FILE, 'a+')
        file.close()

    def is_peer_exist(self, new_peer):
        self.create_peers_if_not_exist()
        new_peer = 'http://' + new_peer
        file = open(PEERS_FILE, 'r+')
        lines = file.readlines()
        for line in lines:
            print(new_peer, line)
            if new_peer == line[:-1]:
                return True
        return False

    def add_node(self, ip):
        if self.is_peer_exist(ip[0]):
            print("[from: node]: Peer already exist")
            return True
        file = open(PEERS_FILE, 'a+')
        print("[from: node]: New peer added: ", ('http://' + ip[0]))
        file.write("%s\n" % ('http://' + ip[0]))
        file.close()
        return True
