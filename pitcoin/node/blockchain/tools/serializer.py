class Serializer:
    def __init__(self, transaction):
        self.ser_tx = None
        self.serialize(transaction)

    def serialize(self, transaction):
        self.ser_tx = transaction.get_amount() +  \
                        transaction.get_sender_address() + \
                        transaction.get_recipient_address() + \
                        transaction.get_verify_key_string() + \
                        transaction.get_sign_string()

    def get_serialized_tx(self):
        return self.ser_tx


class Deserializer:
    def __init__(self, ser_tx):
        self.ser_tx = ser_tx

    def deserialize(self):
        s = self.ser_tx
        return [s[0:4], s[4:39], s[39:74], s[74:202], s[202:]]

