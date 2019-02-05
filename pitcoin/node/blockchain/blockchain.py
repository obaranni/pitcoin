import sys, os, datetime, json, requests
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'blockchain', 'tools'))
from pending_pool import TxPool
from wallet import wifKeyToPrivateKey, fullSettlementPublicAddress, readKeyFromFile, signMessage
from tools.serializer import Deserializer
from serialized_txs_to_json import txs_to_json
from blocks_to_json import convert_blocks_to
from blocks_from_json import convert_last_block_from, convert_by_id_block_from, get_str_block_by_id, convert_block_from
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'classes'))
from block import Block
from transaction import CoinbaseTransaction
TRANSACTIONS_TO_MINE = 4
BASE_COMPLEXITY = 4
MAX_TX_TO_GET = 1000
BLOCKCHAIN_DB = os.path.join(os.path.dirname(__file__),  'storage', 'blocks')
TMP_BLOCKCHAIN_DB = os.path.join(os.path.dirname(__file__),  'storage', 'tmp_blocks')
PEERS_FILE = os.path.join(os.path.dirname(__file__),  'storage', 'peers')


class Blockchain:

    def __init__(self):
        self.blocks = []
        self.mine_mode = False
        self.consensus_mode = False
        self.load_chain()
        self.challenge = True

    def set_configs(self, mine, consensus, peers):
        try:
            print("[from: node]: Configuring a node from a configuration file...")
            if mine == "on":
                self.change_mine_mode()
            if consensus == "on":
                self.change_consensus_mode()
            file = open(PEERS_FILE, 'w+')
            one_line_peers = ''
            for peer in peers:
                one_line_peers += peer + '\n'
            file.write("%s" % one_line_peers)
            file.close()
            print("[from: node]: Configuring done. Current blockchain height:", self.get_chain_length(), end="\n\n")
        except:
            print("[from: node]: Configuring failed!\n")
            return False
        return True

    def change_mine_mode(self):
        self.mine_mode = not self.mine_mode
        if self.mine_mode:
            print("[from: node]: Mining mode: on")
            self.start_mining()
        else:
            print("[from: node]: Mining mode: off")

    def cut_transactions(self):
        tx_pool = TxPool()
        pool_size = tx_pool.get_pool_size()
        if pool_size < TRANSACTIONS_TO_MINE:
            return False
        print("[from: node]: Txs in pool: %d. Start mining" % pool_size)
        txs = tx_pool.get_last_txs(MAX_TX_TO_GET)
        tx_pool.set_txs(txs[TRANSACTIONS_TO_MINE:])
        return txs[:TRANSACTIONS_TO_MINE]

    def send_new_block_alert(self, peers):
        print("\n[from: node]: Reporting to other nodes about new block")
        connections = 0
        for peer in peers:
            try:
                url = 'http://' + peer[:-1] + '/newblock'
                requests.get(url=url)
                connections = 1
            except requests.exceptions.InvalidURL:
                pass
            except requests.exceptions.ConnectionError:
                pass
            except:
                pass
        if connections:
            print("[from: node]: Report completed\n")
        else:
            print("[from: node]: No connection with nodes\n")

    def start_mining(self):
        if len(self.blocks) < 1:
            self.create_chain()
        flag = 0
        self.challenge = True
        while True:
            txs = self.cut_transactions()
            if not txs:
                if flag:
                    break
                return False
            else:
                flag = 1
            if not self.create_block(txs[:TRANSACTIONS_TO_MINE]):
                break
        print("[from: node]: Mining is over. Current blockchain height:", self.get_chain_length())
        self.connect_with_peers(get_chain=False)
        self.challenge = True

    def create_chain(self):
        print("[from: node]: Creating genesis block")
        txs = None
        block = self.mining_hash(self.genesis_block(txs))
        self.save_block(block, BLOCKCHAIN_DB)
        print("[from: node]: Done. Current blockchain height:", self.get_chain_length())

    def load_last_block_from_db(self, db_file, as_str=0):
        self.create_db_if_not_exist(db_file)
        try:
            file = open(db_file, 'r')
            lines = file.readlines()
            file_str = ''
            for line in lines:
                file_str += line
            if len(file_str) > 50:
                block = convert_last_block_from(file_str)
            else:
                block = None
            file.close()
        except:
            return None
        return block

    def lookfor_best_chain(self, lengths):
        best_index = 0
        best_len = -1
        for i in range(0, len(lengths)):
            if int(lengths[i]) > best_len:
                best_len = lengths[i]
                best_index = i
        return best_index

    def take_the_chain_as_own(self, append):
        self.create_db_if_not_exist(BLOCKCHAIN_DB)
        if append:
            new_blocks = open(TMP_BLOCKCHAIN_DB, 'r')
            new_blocks_lines = new_blocks.readlines()
            new_blocks.close()
            old_blocks = open(BLOCKCHAIN_DB, 'a')
            old_blocks.writelines(new_blocks_lines)
            old_blocks.close()
            os.remove(TMP_BLOCKCHAIN_DB)
        else:
            os.remove(BLOCKCHAIN_DB)
            os.rename(TMP_BLOCKCHAIN_DB, BLOCKCHAIN_DB)

    def do_i_need_all_chain(self, peer):
        if len(self.blocks) < 1:
            return 1
        last_block_id = self.blocks[-1].block_id
        try:
            params = (('height', str(last_block_id + 1)),)
            url = 'http://' + peer[:-1] + '/block'
            resp = requests.get(url=url, params=params)
            if resp is None or str(resp.json()).find("error") != -1:
                return 1
            block = convert_block_from((resp.json())['block'])
            if self.blocks[-1].hash == block.hash:
                print("[from: node]: Part of the chains is the same,"
                      " downloading starting from the block", self.blocks[-1].block_id + 1)
                return self.blocks[-1].block_id + 2
            else:
                print("[from: node]: There are no matches in the chains. "
                      "Downloading the chain from scratch")
                return 1
        except requests.exceptions.InvalidURL:
            return 1
        except requests.exceptions.ConnectionError:
            return 1
        except:
            return 1

    def fetch_best_chain(self, peer):
        try:
            i = self.do_i_need_all_chain(peer)
            if i == 1:
                append = 0
            else:
                append = 1
            self.blocks = []
            while True:
                params = (('height', str(i)),)
                url = 'http://' + peer[:-1] + '/block'
                resp = requests.get(url=url, params=params)
                if resp is None or str(resp.json()).find("error") != -1:
                    break
                block = convert_block_from((resp.json())['block'])
                self.save_block(block, TMP_BLOCKCHAIN_DB)
                i += 1
            if self.is_valid_chain(TMP_BLOCKCHAIN_DB):
                print("[from: node]: Chain is valid. Using as own")
                self.take_the_chain_as_own(append)
            else:
                print("[from: node]: Invalid chain! Using own")
                self.blocks = []
                self.blocks = self.load_last_block_from_db(BLOCKCHAIN_DB)
                return False
            print("[from: node]: Fetching done. New chain length:", self.get_chain_length(), end="\n\n")
        except requests.exceptions.InvalidURL:
            print("[from: node]: Failed! Invalid url!")
        except requests.exceptions.ConnectionError:
            print("[from: node]: Failed! Connection error!")
        except:
            print("[from: node]: Failed! Connection error!")

    def peers_chain_lengths(self, peers):
        i = 0
        lengths = []
        connections = 0
        print("[from: node]: Connecting to peers...")
        while i in range(0, len(peers)):
            try:
                peer = peers[i][:-1]
                print("[from: node]: Connecting to peer %s ..." % peer, end="")
                resp = requests.get(url='http://' + peer + '/chain/length', json=[''])
                lengths.append(resp.json()['chain_length'])
                print("  Connected! New peer chain length:", lengths[-1])
                connections = 1
            except requests.exceptions.InvalidURL:
                lengths.append(-1)
                print("  Failed! Invalid url!")
            except requests.exceptions.ConnectionError:
                lengths.append(-1)
                print("  Failed! Connection error!")

            i += 1
        if connections:
            best_index = self.lookfor_best_chain(lengths)
            if int(lengths[best_index]) > self.get_chain_length():
                print("[from: node]: Fetching chain from peer...")
                self.fetch_best_chain(peers[best_index])
                return True
        print("[from: node]: There is no better chain. Using own chain")

    def connect_with_peers(self, get_chain):
        self.create_peers_if_not_exist()
        file = open(PEERS_FILE, 'r')
        peers = file.readlines()
        if get_chain:
            self.peers_chain_lengths(peers)
        else:
            self.send_new_block_alert(peers)
        file.close()

    def load_chain(self):
        print("\n[from: node]: Node started successfully")
        blocks = self.load_last_block_from_db(BLOCKCHAIN_DB)
        print("[from: node]: Loading blocks from database...")
        if blocks is None:
            print("[from: node]: Database is empty")
        else:
            self.blocks = [blocks]
            print("[from: node]: Done")
            print("[from: node]: Chain height:", self.get_chain_length())
        print("[from: node]: Transactions in pool:", TxPool().get_pool_size(), end="\n\n")

        if self.consensus_mode:
            self.connect_with_peers(get_chain=True)
        if self.mine_mode:
            self.create_chain()

    def change_consensus_mode(self):
        self.consensus_mode = not self.consensus_mode
        if self.consensus_mode:
            print("[from: node]: Consensus mode: on")
            self.connect_with_peers(get_chain=True)
        else:
            print("[from: node]: Consensus mode: off")

    def resolve_conflicts(self):
        pass

    def is_valid_chain(self, db_file):
        return True

    def save_blocks(self, db_file):
        self.create_db_if_not_exist(db_file)
        file = open(db_file, 'a+')
        json_blocks = convert_blocks_to(self.blocks)
        for block in json_blocks:
            file.write("%s" % json.dumps(block, indent=4))
        file.write('\n')
        file.close()

    def save_block(self, block, db_file):
        self.blocks.append(block)
        self.blocks = [self.blocks[-1]]
        self.save_blocks(db_file)

    def mining_hash(self, block, complexity=BASE_COMPLEXITY):
        while block.hash[:complexity] != "0" * complexity:
            if not self.challenge:
                return None
            block.nonce += 1
            block.calculate_hash()
        return block

    def create_block(self, txs):
        prev_hash = self.blocks[-1].hash
        block = Block(self.get_timestamp(), prev_hash, txs, self.blocks[-1].block_id + 1)
        block.calculate_merkle_root()
        block.calculate_hash()
        new_block = self.mining_hash(block)
        if new_block is None:
            return False
        self.save_block(new_block, BLOCKCHAIN_DB)
        return True

    def genesis_block(self, txs):
        genesis_block = Block(self.get_timestamp(), "0" * 64, txs, 0)
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

    def create_db_if_not_exist(self, db_file):
        file = open(db_file, 'a+')
        file.close()

    def get_full_blockchain(self, db_file=BLOCKCHAIN_DB):
        self.create_db_if_not_exist(db_file)
        result_line = ''
        file = open(db_file, 'r')
        lines = file.readlines()
        for line in lines:
            result_line += line + '\n'
        file.close()
        return result_line

    def get_chain_length(self):
        if len(self.blocks) == 0:
            return 0
        return self.blocks[-1].block_id + 1

    def get_block_by_id(self, id, db_file=BLOCKCHAIN_DB):
        self.create_db_if_not_exist(db_file)
        if id == -1:
            if len(self.blocks) < 1:
                return None, None
            else:
                id = self.blocks[-1].block_id
        result_line = ''
        file = open(db_file, 'r')
        lines = file.readlines()
        for line in lines:
            result_line += line
        block_json = get_str_block_by_id(result_line, id)
        block = convert_by_id_block_from(result_line, id)
        file.close()
        return block, block_json

    def unpack_txs(self, block, address):
        result = 0
        for i in range(0, len(block.transactions)):
            deser = Deserializer(block.transactions[i])
            p1, p2, p3, p4, p5 = deser.deserialize()
            print(p3, address)
            if p3 == address:
                print("123", result)
                result += 1
        return result



    def get_balance(self, address):
        last = self.blocks[-1].block_id
        current = 0
        for i in range(0, last):
            block, trash = self.get_block_by_id(i)
            current += self.unpack_txs(block, address)
        return current


    def create_peers_if_not_exist(self):
        file = open(PEERS_FILE, 'a+')
        file.close()

    def is_peer_exist(self, new_peer):
        self.create_peers_if_not_exist()
        new_peer = 'http://' + new_peer
        file = open(PEERS_FILE, 'r+')
        lines = file.readlines()
        for line in lines:
            if new_peer == line[:-1]:
                return True
        return False

    def add_node(self, ip):
        if self.is_peer_exist(ip[0]):
            print("[from: node]: Peer already exist")
            return True
        file = open(PEERS_FILE, 'a+')
        print("[from: node]: New peer added: ", ('http://' + ip[0]))
        file.write("%s\n" % (ip[0]))
        file.close()
        if self.consensus_mode:
            self.connect_with_peers(get_chain=True)
        return True
