from binascii import unhexlify
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'classes'))
from Transaction import Transaction
sys.path.append(os.path.join(os.path.dirname(__file__)))
from serializer import  Deserializer
import tx_validator as tx_val

MEMPOOL_FILE = os.path.dirname(__file__) + '/../storage/mempool'


class TxPool:

    def __init__(self):
        pass

    def create_pool_if_not_exist(self):
        file = open(MEMPOOL_FILE, "a+")
        file.close()
    def save_to_mempool(self, set_tx):
        self.create_pool_if_not_exist()
        file = open(MEMPOOL_FILE, "r+")
        first_line = file.readline()
        file.close()
        if len(first_line) < 200:
            file = open(MEMPOOL_FILE, "w+")
        else:
            file = open(MEMPOOL_FILE, "a+")
        file.write("%s\n" % set_tx)
        file.close()

    def new_transaction(self, ser_tx):
        # data = Deserializer(ser_tx).deserialize()
        # tx = Transaction(data[1], data[2], data[0])
        # tx.calculate_hash()
        # tx.set_sign(unhexlify(data[4]), data[3])
        # if not tx_val.validate_signature(tx, data[3]):
        #     return False
        # if not tx_val.validate_recipient_address(tx.get_unformat_recipient_address()):
        #     return False
        # if not tx_val.validate_recipient_address(tx.get_unformat_sender_address()):
        #     return False
        # self.save_to_mempool(ser_tx)
        try:
            tx = Transaction(False, False)
            tx.set_signed_raw_tx(ser_tx)
            print(tx.deserialize_raw_tx())
            self.save_to_mempool(ser_tx)
        except:
            print("[from: node]: transaction was not added")
            return False
        return True

    def get_last_txs(self, count):
        self.create_pool_if_not_exist()
        file = open(MEMPOOL_FILE, "r")
        all_lines = file.readlines()
        last_lines = []
        while count > 0:
            if count <= len(all_lines):
                last_lines.append(all_lines[-count][:-1])
            count -= 1
        file.close()
        return last_lines

    def get_pool_size(self):
        self.create_pool_if_not_exist()
        file = open(MEMPOOL_FILE, "r")
        result = sum(1 for line in file)
        file.close()
        return result

    def set_txs(self, txs):
        self.create_pool_if_not_exist()
        file = open(MEMPOOL_FILE, "w+")
        for tx in txs:
            file.write("%s\n" % tx)
        file.close()

