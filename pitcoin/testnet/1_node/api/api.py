from flask import  Flask, request, jsonify
import sys, os, json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'blockchain'))
from blockchain import Blockchain
import logging, threading, time
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
# Create the application instance
app = Flask(__name__)
app.config['DEBUG'] = False



# node = None

status_codes = {
    "Transaction pull i empty": 101,
    "Node added": 102,
    "Cannot start mine mode": 103,
    "Transaction pended": 201,
    "Bad json format": 401,
    "Bad transaction": 402,
}

node = None
CONFIG_FILE = os.path.join(os.path.dirname(__file__),  '..', 'config')


class NonJSON(Exception):
    pass

class EmptyPool(Exception):
    pass


@app.route('/mine', methods=['GET'])
def set_mine():
    global node

    node.change_mine_mode()
    if node.mine_mode:
        return jsonify('[from: node]: mining mode on')
    return jsonify('[from: node]: mining mode off')


@app.route('/consensus', methods=['GET'])
def set_consensus():
    global node

    node.change_consensus_mode()
    if node.consensus_mode:
        return jsonify('[from: node]: consensus mode on')
    return jsonify('[from: node]: consensus mode off')


@app.route('/newblock', methods=['GET'])
def new_block():
    global node
    node.challenge = False
    if node.consensus_mode:
        print("[from: node]: Someone mined a new block")
        node.get_new_block_alert()
    else:
        print("\n[from: node]: Someone mined a new block")
        print("[from: node]: please run consensus mode to fetch bigger chain")
    return jsonify('Done')


@app.route('/difficulty', methods=['GET'])
def get_difficulty():
    global node
    request.args.get('address')
    difficulty = node.get_difficulty()
    if not difficulty:
        return jsonify({'difficulty': 'Error'})
    return jsonify({'difficulty': difficulty})

@app.route('/utxo', methods=['GET'])
def get_utxo():
    global node
    address = request.args.get('address')

    utxo = node.get_utxo(address)
    if not utxo:
        return jsonify({'utxo': 'Error utxo for ' + address + ' doesn\'t exist'})
    return jsonify({'utxo': utxo})

@app.route('/addnode', methods=['POST'])
def add_node():
    global node
    try:
        if not request.is_json:
            raise NonJSON
        data = request.get_json()
        if not node.add_node(data['node_ip']):
            return jsonify(''), status_codes['Bad node ip']
    except NonJSON:
        print("Not json request! Declined!")
        return jsonify(''), status_codes['Bad json format']
    return jsonify(''), status_codes['Node added']


@app.route('/chain/length', methods=['GET'])
def get_chain_length():
    global node
    return jsonify({'chain_length': node.get_chain_length()})


@app.route('/block/last', methods=['GET'])
def get_last_block():
        global node
        block, block_str = node.get_block_by_id(id=-1)
        if not block:
            return jsonify({'block': 'None', 'error': 'Chain is empty'})
        return jsonify({'block': block_str})


@app.route('/block', methods=['GET'])
def get_block():
        global node
        height = request.args.get('height')
        if height is None or not height.isdigit() or int(height) < 1:
            return jsonify({'block': 'None', 'error:':'block height should be a positive number above zero, '
                                                      '\"/block?height=28\"'})
        block, block_str = node.get_block_by_id(int(height) - 1)
        if not block:
            return jsonify({'block': 'None', 'error': 'Block doesn\'t exist'})
        return jsonify({'block': block_str})


@app.route('/balance', methods=['GET'])
def get_balance():
        global node
        address = request.args.get('address')
        if address is None or len(address) < 26:
            return jsonify({'balance': 'None', 'error:':'bad address'})
        balance = node.get_balance(address)
        return jsonify({'balance': balance})

@app.route('/chain', methods=['GET'])
def get_full_chain():
    return node.get_full_blockchain()


@app.route('/transaction/pendings', methods=['GET', 'POST'])
def get_pending_transactions():
    global node
    try:
        txs = node.get_pending_txs()
        if len(txs) < 3:
            raise EmptyPool
    except EmptyPool:
        return jsonify("Transaction pull i empty")
    return txs


@app.route('/transaction/new', methods=['POST', 'HTTP'])
def set_new_transaction():
    global node
    try:
        if not request.is_json:
            raise NonJSON
        data = request.get_json()
        if not node.submit_tx(data['serialized_tx']):
            return jsonify(''), status_codes['Bad transaction']
    except NonJSON:
        print("Not json request! Declined!")
        return jsonify(''), status_codes['Bad json format']
    return jsonify(''), status_codes['Transaction pended']


def print_bad_config():
    print("[from: node]: Failed!")
    print("[from: node]: Bad json format in config file!")
    print("[from: node]: Example:\n{\n\t\"host_ip\": \n\t\""
          "127.0.0.1:5000\",\n\t\"mining_mode\": \"off\",\n"
          "\t\"consensus_mode\": \"off\",\n\t\"trusted_peer"
          "s\": [\n\t\t\"127.0.0.1:5010\",\n\t\t\"127.0.0.1:"
          "5011\",\n\t\t\"127.0.0.1:5012\"\n\t]\n}")


def start_server(host, port):
    app.run(host=host, port=port, threaded=True)


def start_mining():
    global node
    node.start_mining()


class MiningThread(threading.Thread):
    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.counter = counter

    def run(self):
        start_mining()


class ServerThread(threading.Thread):
    def __init__(self, thread_id, name, counter, host, port):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.counter = counter
        self.host = host
        self.port = port

    def run(self):
        start_server(self.host, self.port)


def main():
    global node
    if not os.path.exists(CONFIG_FILE):
        print("[from: node]: Failed!")
        print("[from: node]: Create config file first!")
        return False
    try:
        conf_file = open(CONFIG_FILE, 'r')
        config = json.load(conf_file)
        conf_file.close()
        host = config['host_ip'].split(':')[0]
        port = config['host_ip'].split(':')[1]
        cons = config['consensus_mode']
        mine = config['mining_mode']
        peers = config['trusted_peers']
        node = Blockchain()
        if not node.set_configs(mine, cons, peers):
            print("[from: node]: Bad configuration file parameters!")
            return False
        node.start_node()
    except json.decoder.JSONDecodeError:
        print_bad_config()
        return False

    server_thread = ServerThread(1, "Server Thread", 1, host=host, port=port)
    mining_thread = MiningThread(2, "Mining Thread", 2)

    server_thread.start()
    # time.sleep(2) #wating for genesis block
    mining_thread.start()

    mining_thread.join()
    server_thread.join()



if __name__ == '__main__':
    main()
