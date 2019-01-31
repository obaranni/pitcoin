from flask import  Flask, request, jsonify
import sys, os, json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'blockchain'))
from blockchain import Blockchain


# Create the application instance
app = Flask(__name__)
app.config['DEBUG'] = True
# Create a URL route in our application for "/"

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
    print("[from: node]: someone mined a new block")
    if node.consensus_mode:
        node.connect_with_peers(get_chain=True)
    else:
        print("[from: node]: please run consensus mode to fetch bigger chain")
    return jsonify('Done')


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


@app.route('/getblock', methods=['GET'])
def get_block():
        global node
        id = request.args.get('id')
        if id is None or not id.isdigit() or int(id) < 0:
            return jsonify({'block': 'None', 'error:':'block id should be a positive number, \"/getblock?id=28\"'})
        block, block_str = node.get_block_by_id(id)
        if not block:
            return jsonify({'block': 'None', 'error': 'Block doesn\'t exist'})
        return jsonify({'block': block_str})


@app.route('/chain', methods=['GET'])
def get_full_chain():
    return jsonify('Please use /getblock?id=*iterator* to get all blocks')


@app.route('/transaction/pendings')
def get_pending_transactions():
    global node
    try:
        txs = node.get_pending_txs()
        if len(txs) < 3:
            code = status_codes["Transaction pull i empty"]
            raise Exception
    except:
        return jsonify("Transaction pull i empty"), status_codes["Transaction pull i empty"]
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
    except json.decoder.JSONDecodeError:
        print_bad_config()
        return False
    app.run(host=host, port=port)


if __name__ == '__main__':
    main()