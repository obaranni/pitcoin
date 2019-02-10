import sys, os, datetime, json, requests, base58, hashlib, codecs
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'blockchain', 'tools'))
from pending_pool import TxPool
from wallet import wifKeyToPrivateKey, fullSettlementPublicAddress, readKeyFromFile, signMessage, getAddresOfPublicKey
from serialized_txs_to_json import txs_to_json
from blocks_to_json import convert_blocks_to
from blocks_from_json import convert_last_block_from, convert_by_id_block_from, get_str_block_by_id, convert_block_from
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'classes'))
from block import Block
from Transaction import CoinbaseTransaction, Transaction
TRANSACTIONS_TO_MINE = 1
BASE_COMPLEXITY = 4
MAX_TX_TO_GET = 1000
BLOCKCHAIN_DB = os.path.join(os.path.dirname(__file__),  'storage', 'blocks')
TMP_BLOCKCHAIN_DB = os.path.join(os.path.dirname(__file__),  'storage', 'tmp_blocks')
PEERS_FILE = os.path.join(os.path.dirname(__file__),  'storage', 'peers')
UTXO_FILE = os.path.join(os.path.dirname(__file__),  'storage', 'utxo')
TMP_UTXO_FILE = os.path.join(os.path.dirname(__file__),  'storage', 'tmp_utxo')

class Blockchain:

    def __init__(self):
        self.blocks = []
        self.mine_mode = False
        self.consensus_mode = False
        self.load_chain()
        self.challenge = True

    def set_configs(self, mine, consensus, peers):
        # try:
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
        # except:
        #     print("[from: node]: Configuring failed!\n")
        #     return False
            return True

    def change_mine_mode(self):
        self.mine_mode = not self.mine_mode
        if self.mine_mode:
            print("[from: node]: Mining mode: on")
            self.start_mining()
        else:
            print("[from: node]: Mining mode: off")

    def execute_script(self, tx, output):
        return True

    def verify_tx(self, raw_tx, utxo_flags):
        tx = Transaction(False, False)
        tx.set_signed_raw_tx(raw_tx)
        tx_dict = json.loads(tx.deserialize_raw_tx())
        print(tx_dict)
        tx_inputs = []
        for j in tx_dict['inputs']:
            output_tx_id = j['prev_tx_id']
            output_id = j['out_index']
            tx_inputs.append({'output_tx_id': output_tx_id,'output_id': output_id})

        inputs_amount = 0
        for j in tx_inputs:
            input_found = 0
            for utxo_flag in utxo_flags:
                if j['output_tx_id'] == utxo_flag[0]['tx_id'] and j['output_id'] == utxo_flag[0]['output_id']:
                    input_found = 1
                    if utxo_flag[1] == 1:
                        print("[from: node]: BAD TX! INPUT ALREADY SPENT")
                        return False
                    utxo_flag[1] = 1
                inputs_amount += float(utxo_flag[0]['value'])
            if not input_found:
                print("[from: node]: BAD TX! CANNOT FIND INPUT!")
                return False

        outputs_amount = 0.0
        for i in tx_dict['outputs']:
            outputs_amount += float(i['value'])
        if outputs_amount > inputs_amount:
            print("[from: node]: BAD TX! OUTPUTS VALUE SHOULD BE GREATER THAN INPUTS!")
            return False
        print("amount of inputs", inputs_amount, "amount of outputs", outputs_amount)
        if not self.execute_script(tx, "out"):
            return False
        return True

    def cut_transactions(self):
        tx_pool = TxPool()
        pool_size = tx_pool.get_pool_size()
        if pool_size < TRANSACTIONS_TO_MINE:
            return False
        print("[from: node]: Txs in pool: %d. Start mining" % pool_size)
        txs = tx_pool.get_last_txs(MAX_TX_TO_GET)
        valid_txs = []
        utxo = self.get_utxo("address")
        utxo_flags = []
        for i in utxo:
            utxo_flags.append([i, 0])
        for tx in txs:
            if self.verify_tx(tx, utxo_flags):
                valid_txs.append(tx)
        if len(valid_txs) < TRANSACTIONS_TO_MINE and len(valid_txs) > 0:
            tx_pool.set_txs(valid_txs)
            return False
        utxo_file = open(UTXO_FILE, "w+")
        for i in utxo_flags:
            if i[1] == 0:
                utxo_file.write("%s\n" % str(i[0]))



        txs_to_mine = valid_txs[:TRANSACTIONS_TO_MINE]


        tx_pool.set_txs(valid_txs[TRANSACTIONS_TO_MINE:])
        utxo_file.close()
        return txs_to_mine

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

    def create_utxo_if_not_exit(self, utxo_file_path=UTXO_FILE):
        utxo_file = open(utxo_file_path, "a+")
        utxo_file.close()

    def get_balance(self, address):
        utxo = self.get_utxo(address)
        balance = 0
        if not utxo:
            return balance
        for i in utxo:
            balance += float(i['value'])
        return balance

    def get_utxo(self, address, utxo_file_path=UTXO_FILE):
        self.create_utxo_if_not_exit(utxo_file_path)
        print("PATH", utxo_file_path)
        utxo_file = open(utxo_file_path, "r")
        lines = utxo_file.readlines()
        print(lines)
        address_utxo = []
        for line in lines:
            if line.find(address) != -1:
                line = line[:-1].replace('\'', '"')
                utxo_dict = json.loads(line)
                address_utxo.append(utxo_dict)
        utxo_file.close()
        print(address_utxo)
        if len(address_utxo) > 0:
            return address_utxo
        else:
            return False

    def calculate_utxo(self, block, utxo_file_path=UTXO_FILE, del_old=0, save=1):
        self.create_utxo_if_not_exit(utxo_file_path)
        if del_old:
            utxo_file = open(utxo_file_path, "w+")
        else:
            utxo_file = open(utxo_file_path, "a+")
        utxos_dict = []
        result_outputs_dict = ""
        for i in block.transactions:
            tx = Transaction(False, False)
            tx.set_signed_raw_tx(i)
            tx_outputs_dict = json.loads(tx.deserialize_raw_tx())['outputs']
            out_id = 0
            for j in tx_outputs_dict:
                j['address'] = base58.b58encode_check(bytes.fromhex('6f' + j['script'][6:46])).decode('utf-8')
                j['tx_id'] = hashlib.sha256(hashlib.sha256(bytes.fromhex(i)).digest()).hexdigest()
                j['output_id'] = out_id
                utxos_dict.append(j)
                result_outputs_dict += str(j) + "\n"
                out_id += 1
        if save:
            utxo_file.write("%s" % result_outputs_dict)
        utxo_file.close()
        if len(utxos_dict) < 1:
            return False
        else:
            return utxos_dict

    def create_chain(self):
        print("[from: node]: Creating genesis block")
        txs = None
        block = self.mining_hash(self.genesis_block(txs))
        self.save_block(block, BLOCKCHAIN_DB)
        self.calculate_utxo(self.blocks[-1], UTXO_FILE, del_old=1)
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
        self.create_utxo_if_not_exit(UTXO_FILE)
        if append > 1:
            new_blocks = open(TMP_BLOCKCHAIN_DB, 'r')
            new_blocks_lines = new_blocks.readlines()
            new_blocks.close()
            old_blocks = open(BLOCKCHAIN_DB, 'a')
            old_blocks.writelines(new_blocks_lines)
            old_blocks.close()
            os.remove(TMP_BLOCKCHAIN_DB)
            new_utxo = open(TMP_UTXO_FILE, 'r')
            new_utxo_lines = new_utxo.readlines()
            new_utxo.close()
            old_utxo = open(UTXO_FILE, 'a')
            old_utxo.writelines(new_utxo_lines)
            old_utxo.close()
            os.remove(TMP_UTXO_FILE)
        else:
            os.remove(UTXO_FILE)
            os.rename(TMP_UTXO_FILE, UTXO_FILE)
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
        # try:
            i = self.do_i_need_all_chain(peer)
            print("ska", i)
            append = i
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
            if self.is_valid_chain(TMP_BLOCKCHAIN_DB, TMP_UTXO_FILE, append - 1):
                print("[from: node]: Chain is valid. Using as own")
                self.take_the_chain_as_own(append)
            else:
                print("[from: node]: Invalid chain! Using own")
                self.blocks = []
                self.blocks = self.load_last_block_from_db(BLOCKCHAIN_DB)
                return False
            print("[from: node]: Fetching done. New chain length:", self.get_chain_length(), end="\n\n")
        # except requests.exceptions.InvalidURL:
        #     print("[from: node]: Failed! Invalid url!")
        # except requests.exceptions.ConnectionError:
        #     print("[from: node]: Failed! Connection error!")
        # except:
        #     print("[from: node]: Failed! Connection error!")

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

    def is_valid_chain(self, db_file, utxo_file_path, block_id=0):
        self.create_db_if_not_exist(db_file)
        block_count = block_id
        print(block_id)

        while True:
            block, block_json = self.get_block_by_id(block_count, db_file)
            print(block_json)
            if not block:
                break



            old_utxo = self.get_utxo("address", utxo_file_path)
            print(old_utxo)
            if old_utxo:
                old_utxo_flags = [[i, 0] for i in old_utxo]
                print("o1", old_utxo_flags)
                for tx in block.transactions:
                    if tx != block.transactions[-1]:
                        if not self.verify_tx(tx, old_utxo_flags):
                            return False
                print("o2", old_utxo_flags)
            else:
                old_utxo_flags = False



            if old_utxo_flags:
                # print("o1", old_utxo_flags)
                utxo_file = open(utxo_file_path, "w+")
                for i in old_utxo_flags:
                    if i[1] == 0:
                        utxo_file.write("%s\n" % str(i[0]))
                utxo_file.close()
            else:
                utxo_file = open(utxo_file_path, "w+")
                utxo_file.close()




            new_utxo = self.calculate_utxo(block, utxo_file_path, save=0)
            if new_utxo:
                # print("o2", new_utxo)
                utxo_file = open(utxo_file_path, "a+")
                for i in new_utxo:
                    if i:
                        utxo_file.write("%s\n" % str(i))
                utxo_file.close()

            block_count += 1
        return True

    def save_blocks(self, db_file):
        self.create_db_if_not_exist(db_file)
        file = open(db_file, 'a+')
        json_blocks = convert_blocks_to(self.blocks)
        for block in json_blocks:
            file.write("%s" % json.dumps(block, indent=4))
        file.write('\n')
        file.close()

    def save_block(self, block, db_file, del_old=0):
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
        self.save_block(new_block, BLOCKCHAIN_DB, UTXO_FILE)
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
        file.close()
        for line in lines:
            result_line += line
        block_json = get_str_block_by_id(result_line, id)
        block = convert_by_id_block_from(result_line, id)
        return block, block_json

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
