from flask import  Flask, request, jsonify

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'blockchain'))
from blockchain import Blockchain


# Create the application instance
app = Flask(__name__)
app.config['DEBUG'] = True

# Create a URL route in our application for "/"

# node = None

status_codes = {
    "Transaction pull i empty": 101,
    "Transaction pended": 201,
    "Bad json format": 401,
    "Bad transaction": 402,
}

class NonJSON(Exception):
    pass

node = Blockchain()

@app.route('/mine', methods=['POST', 'GET', 'HTTP'])
def set_mine():
    global node
    node.change_mine_mode()
    if node.mine_mode:
        return jsonify('[from: node]: mining mode on')
    return jsonify('[from: node]: mining mode off')


@app.route('/chain')
def get_full_chain():
    global node

    pass

@app.route('/transaction/pendings')
def get_pending_transactions():
    global node
    code = None
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

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run()