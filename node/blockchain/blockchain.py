from node.blockchain.tools.pending_pool import TxPool

BASE_COMPLEXITY = 2


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
        TxPool().new_transaction(new_tx)
