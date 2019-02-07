import hashlib, base58, ecdsa, json, struct
from enum import Enum
from ecdsa.util import string_to_number, number_to_string
from ecdsa.curves import SECP256k1
from .Input import Input
from .Output import Output

CURVE_ORDER = SECP256k1.order

DECIMALS = 8
MAX_AMOUNT = 21000000
ADDRESS_LEN = 35



class AmountError(Exception):
    pass


# TODO:                check input_values - output_values >= 0

class Transaction:
    def __init__(self, inputs, outputs, version=1, locktime=0):
        # try:
            self.version = struct.pack("<L", version)
            self.numb_inputs = struct.pack("<B", 0)
            self.numb_outputs = struct.pack("<B", 0)
            self.inputs = []
            self.outputs = []
            self.create_inputs(inputs)
            self.create_outputs(outputs)
            self.locktime = struct.pack("<L", locktime)
            self.raw_tx = []
            self.real_raw_tx = None
            self.tx_hashes = []
            self.signs = []
        # except:
        #     print("Bad inputs or outputs")

    def validate_input(self, input):
        return True

    def create_inputs(self, inputs):
        # try:
            inputs_dict = json.loads(inputs)['inputs']
            inputs_arr = [i for i in inputs_dict]
            for i in inputs_arr:
                self.validate_input(i)
                self.inputs.append(Input(i['tx_id'], i['tx_out_id'], i['tx_script']))
            self.numb_inputs = struct.pack("<B", len(self.inputs))
        # except:
        #     print("Bad input")

    def validate_output(self, input):
        amount = input['value']
        if float(amount) > MAX_AMOUNT or len(str(amount).split('.')[1]) > DECIMALS:
            raise AmountError
        input['value'] = int(float(amount) * int(pow(10, DECIMALS)))

    def create_outputs(self, outputs):
        # try:
            outputs_dict = json.loads(outputs)['outputs']
            outputs_arr = [i for i in outputs_dict]
            for i in outputs_arr:
                self.validate_output(i)
                self.outputs.append(Output(i['address'], i['value'], i['script_type']))
            self.numb_outputs = struct.pack("<B", len(self.outputs))
        # except:
        #     print("Bad input")

    def get_presign_raw_inputs(self, input_id):
        raw_inputs = b''
        for i in range(0, len(self.inputs)):
            if i == input_id:
                raw_inputs += self.inputs[i].get_presign_raw_format()
            else:
                raw_inputs += self.inputs[i].get_presign_zero_script_raw_format()
        return raw_inputs

    def get_sign_raw_inputs(self, compressed_pub_key):
        raw_inputs = b''
        for i in range(0, len(self.inputs)):
            raw_inputs += self.inputs[i].get_sign_raw_format(self.signs[i], compressed_pub_key)
        return raw_inputs

    def get_raw_outputs(self):
        raw_outputs = b''
        for i in self.outputs:
            raw_outputs += i.get_raw_format()
        return raw_outputs

    def get_presign_raw_format(self):
        for i in range(0, len(self.inputs)):
            self.raw_tx.append(
                self.version
                + self.numb_inputs
                + self.get_presign_raw_inputs(i)
                + self.numb_outputs
                + self.get_raw_outputs()
                + self.locktime
                + struct.pack("<L", 1)
            )
        return self.raw_tx

    def get_signed_raw_format(self, compressed_pub_key):
        self.real_raw_tx = (
                self.version
                + self.numb_inputs
                + self.get_sign_raw_inputs(compressed_pub_key)
                + self.numb_outputs
                + self.get_raw_outputs()
                + self.locktime
        )
        return self.real_raw_tx

    def calculate_hash(self):
        for i in range(0, len(self.inputs)):
            self.tx_hashes.append(hashlib.sha256(hashlib.sha256(self.raw_tx[i]).digest()).digest())
        return self.tx_hashes

    def sign_tx(self, priv_key):
        priv_key_bytes = bytes.fromhex(priv_key)
        sk = ecdsa.SigningKey.from_string(priv_key_bytes, curve=ecdsa.SECP256k1)
        for i in range(0, len(self.inputs)):
            self.signs.append(sk.sign_digest(self.tx_hashes[i], sigencode=ecdsa.util.sigencode_der_canonize))
        return self.signs


class CoinbaseTransaction(Transaction): # TODO: as above tx
    # def __init__(self, recipient, amount=50):
    #     self.recipient = recipient
    #     self.amount = amount
    pass


def ripemd160(x):
    d = hashlib.new('ripemd160')
    d.update(x)
    return d


class Network(Enum):
    TEST_NET = 0
    PROD_NET = 1


def flip_byte_order(string):
    flipped = "".join(reversed([string[i:i + 2] for i in range(0, len(string), 2)]))
    return flipped


def normalize_secret_bytes(privkey_bytes: bytes) -> bytes:
    scalar = string_to_number(privkey_bytes) % CURVE_ORDER
    if scalar == 0:
        raise Exception('invalid EC private key scalar: zero')
    privkey_32bytes = number_to_string(scalar, CURVE_ORDER)
    return privkey_32bytes
