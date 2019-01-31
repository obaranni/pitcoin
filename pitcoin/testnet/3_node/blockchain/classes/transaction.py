import hashlib

DECIMALS = 1
ADDRESS_LEN = 35
AWARD = 50
COINBASE_SENDER = "0000000000000000000000000000000000000000000000000000000000000000"

class Transaction:

    def __init__(self, sender, recipient, amount):
        self.sender = self.format_address(sender)
        self.recipient = self.format_address(recipient)
        self.amount = amount
        self.raw_tx = self.sender + self.recipient + amount
        self.verification_key = None
        self.hash = None
        self.sign = None

    def set_sign(self, sign, verification_key):
        self.verification_key = verification_key
        self.sign = sign

    def calculate_hash(self): # sha256 of bytes representation sender+recipient+amount
        self.hash = hashlib.sha256(bytes(self.raw_tx.encode('utf-8'))).hexdigest()

    def get_hash(self):
        return self.hash

    def get_sender_address(self):
        return self.sender

    def get_recipient_address(self):
        return self.recipient

    def get_sign(self):
        return self.sign

    def get_raw_tx(self):
        return self.raw_tx

    def get_amount(self):
        return self.amount

    def get_verify_key(self):
        return self.verification_key

    def get_verify_key_string(self):
        return self.verification_key.to_string().hex()

    def get_sign_string(self):
        return self.sign.hex()

    def format_address(self, address):
        while len(address) < ADDRESS_LEN:
            address = "0" + address
        return address

    def unformat_address(self, address):
        i = 0
        while address[i] == '0' and len(address[i:]) > 26:
            i += 1
        return i

    def get_unformat_recipient_address(self):
        return self.recipient[self.unformat_address(self.recipient):]

    def get_unformat_sender_address(self):
        return self.sender[self.unformat_address(self.sender):]



class CoinbaseTransaction(Transaction):
    def __init__(self, recipient, amount=AWARD):
        amount = "{0:0{1}x}".format(int(amount), 4)
        Transaction.__init__(self, COINBASE_SENDER, recipient, amount)
    pass
