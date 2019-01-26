from node.blockchain.tools.serializer import Deserializer
from binascii import unhexlify
from node.blockchain.classes.transaction import Transaction
from node.blockchain.tools import tx_validator as tx_val

MEMPOOL_FILE = 'node/blockchain/storage/mempool'


class TxPool:

    def __init__(self):
        pass

    def save_to_mempool(self, set_tx):
        file = open(MEMPOOL_FILE, "a+")
        file.write("%s\n" % set_tx)
        file.close()

    def new_transaction(self, ser_tx):
        data = Deserializer(ser_tx).deserialize()
        tx = Transaction(data[1], data[2], data[0])
        tx.calculate_hash()
        tx.set_sign(unhexlify(data[4]), data[3])
        if not tx_val.validate_signature(tx, data[3]):
            return False
        if not tx_val.validate_recipient_address(tx.get_unformat_recipient_address()):
            return False
        if not tx_val.validate_recipient_address(tx.get_unformat_sender_address()):
            return False
        self.save_to_mempool(ser_tx)
        return True

    def get_last_txs(self, count):
        file = open(MEMPOOL_FILE, "r+")
        all_lines = file.readlines()
        last_lines = []
        while count > 0:
            if count <= len(all_lines):
                last_lines.append(all_lines[-count][:-1])
            count -= 1
        file.close()
        return last_lines
