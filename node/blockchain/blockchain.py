import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'blockchain', 'tools'))
from pending_pool import TxPool
from serialized_txs_to_json import txs_to_json

BASE_COMPLEXITY = 2
MAX_TX_TO_GET = 1000

class Blockchain:
    def __init__(self):
        pass

    def mine(self, complexity=BASE_COMPLEXITY):
        pass

    def resolve_conflicts(self):
        pass

    def is_valid_chain(self):
        pass

    def add_node(self):
        pass

    def genesis_block(self):
        pass

    def submit_tx(self, new_tx):
        return TxPool().new_transaction(new_tx)

    def get_pending_txs(self):
        return txs_to_json(TxPool().get_last_txs(MAX_TX_TO_GET))
