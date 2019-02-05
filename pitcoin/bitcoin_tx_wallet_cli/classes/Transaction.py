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
            self.raw_tx = None
            self.real_raw_tx = None
            self.tx_hash = None
            self.sign = None
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
        amount = float(input['value'])
        if amount > MAX_AMOUNT or len(str(amount).split('.')[1]) > DECIMALS:
            print(123123)
            raise AmountError
        input['value'] = int(amount * int(pow(10, DECIMALS)))

    def create_outputs(self, outputs):
        # try:
            outputs_dict = json.loads(outputs)['outputs']
            outputs_arr = [i for i in outputs_dict]
            for i in outputs_arr:
                self.validate_output(i)
                self.outputs.append(Output(i['address'], i['value'], i['script_type']))
            self.numb_outputs = struct.pack("<B", len(self.outputs))
            print(len(self.outputs), self.numb_outputs)
        # except:
        #     print("Bad input")

    def get_presign_raw_inputs(self):
        raw_inputs = b''
        for i in self.inputs:
            raw_inputs += i.get_presign_raw_format()
        return raw_inputs

    def get_sign_raw_inputs(self, compressed_pub_key):
        raw_inputs = b''
        for i in self.inputs:
            raw_inputs += i.get_sign_raw_format(self.sign, compressed_pub_key)
        return raw_inputs

    def get_raw_outputs(self):
        raw_outputs = b''
        for i in self.outputs:
            raw_outputs += i.get_raw_format()
        return raw_outputs

    def get_presign_raw_format(self):
        self.raw_tx = (
                self.version
                + self.numb_inputs
                + self.get_presign_raw_inputs()
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
        self.tx_hash = hashlib.sha256(hashlib.sha256(self.raw_tx).digest()).digest()
        return self.tx_hash

    def sign_tx(self, priv_key):
        priv_key_bytes = bytes.fromhex(priv_key)
        sk = ecdsa.SigningKey.from_string(priv_key_bytes, curve=ecdsa.SECP256k1)
        self.sign = sk.sign_digest(self.tx_hash, sigencode=ecdsa.util.sigencode_der_canonize)
        return self.sign


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

"""
class raw_tx:
    version = struct.pack("<L", 1)
    tx_in_count = struct.pack("<B", 1)
    tx_in = {}  # TEMP
    tx_out_count = struct.pack("<B", 2)
    tx_out1 = {}  # TEMP
    tx_out2 = {}  # TEMP
    lock_time = struct.pack("<L", 0)
"""


def flip_byte_order(string):
    flipped = "".join(reversed([string[i:i + 2] for i in range(0, len(string), 2)]))
    return flipped


def normalize_secret_bytes(privkey_bytes: bytes) -> bytes:
    scalar = string_to_number(privkey_bytes) % CURVE_ORDER
    if scalar == 0:
        raise Exception('invalid EC private key scalar: zero')
    privkey_32bytes = number_to_string(scalar, CURVE_ORDER)
    return privkey_32bytes

# def make_raw_transaction():
    # rtx = raw_tx()
    #
    # my_address = sender_address
    # my_hashed_pubkey = base58.b58decode_check(my_address)[1:].hex()
    #
    # my_private_key = sender_wif_priv
    # my_private_key_hex = base58.b58decode_check(my_private_key)[1:33].hex()
    #
    # recipient = recipient_address
    # recipient_hashed_pubkey = base58.b58decode_check(recipient)[1:].hex()
    #
    # my_output_tx = prev_txid
    # input_value = input_amount
    # form tx_in







    # rtx.tx_in["txouthash"] = bytes.fromhex(flip_byte_order(my_output_tx))
    # rtx.tx_in["tx_out_index"] = struct.pack("<L", 1)
    # rtx.tx_in["script"] = bytes.fromhex("76a914%s88ac" % my_hashed_pubkey)
    # rtx.tx_in["scrip_bytes"] = struct.pack("<B", len(rtx.tx_in["script"]))
    # rtx.tx_in["sequence"] = bytes.fromhex("ffffffff")



    # form tx_out
    # rtx.tx_out1["value"] = struct.pack("<Q", output_amount)
    # rtx.tx_out1["pk_script"] = bytes.fromhex("76a914%s88ac" % recipient_hashed_pubkey)
    # rtx.tx_out1["pk_script_bytes"] = struct.pack("<B", len(rtx.tx_out1["pk_script"]))
    #
    # return_value = input_value - output_amount - fee # 1000 left as fee
    # rtx.tx_out2["value"] = struct.pack("<Q", return_value)
    # rtx.tx_out2["pk_script"] = bytes.fromhex("76a914%s88ac" % my_hashed_pubkey)
    # rtx.tx_out2["pk_script_bytes"] = struct.pack("<B", len(rtx.tx_out2["pk_script"]))
    # =========================================
    # form raw_tx
    # raw_tx_string = (
    #         rtx.version
    #         + rtx.tx_in_count
    #         + rtx.tx_in["txouthash"]
    #         + rtx.tx_in["tx_out_index"]
    #         + rtx.tx_in["scrip_bytes"]
    #         + rtx.tx_in["script"]
    #         + rtx.tx_in["sequence"]
    #         + rtx.tx_out_count
    #         + rtx.tx_out1["value"]
    #         + rtx.tx_out1["pk_script_bytes"]
    #         + rtx.tx_out1["pk_script"]
    #         + rtx.tx_out2["value"]
    #         + rtx.tx_out2["pk_script_bytes"]
    #         + rtx.tx_out2["pk_script"]
    #         + rtx.lock_time
    #         + struct.pack("<L", 1)
    # )

    # hashed_tx_to_sign = hashlib.sha256(hashlib.sha256(raw_tx_string).digest()).digest()




    # pk_bytes = bytes.fromhex(my_private_key_hex)
    # sk = ecdsa.SigningKey.from_string(pk_bytes, curve=ecdsa.SECP256k1)
    # vk = sk.verifying_key

    # can be used for uncompressed pubkey
    # vk_string = vk.to_string()
    # public_key_bytes = b'\04' + vk_string

    # public_key_bytes_hex = sender_compressed_pub
    #
    # signature = sk.sign_digest(hashed_tx_to_sign, sigencode=ecdsa.util.sigencode_der_canonize)

    # sigscript = (
    #
    #         signature
    #         + b'\01'
    #         + struct.pack("<B", len(bytes.fromhex(public_key_bytes_hex)))
    #         + bytes.fromhex(public_key_bytes_hex)
    #
    # )
    #
    # real_tx = (
    #         rtx.version
    #         + rtx.tx_in_count
    #         + rtx.tx_in["txouthash"]
    #         + rtx.tx_in["tx_out_index"]
    #         + struct.pack("<B", len(sigscript) + 1)
    #         + struct.pack("<B", len(signature) + 1)
    #         + sigscript
    #         + rtx.tx_in["sequence"]
    #         + rtx.tx_out_count
    #         + rtx.tx_out1["value"]
    #         + rtx.tx_out1["pk_script_bytes"]
    #         + rtx.tx_out1["pk_script"]
    #         + rtx.tx_out2["value"]
    #         + rtx.tx_out2["pk_script_bytes"]
    #         + rtx.tx_out2["pk_script"]
    #         + rtx.lock_time
    #
    # )
    # print("raw_tx " + '=' * 30)
    # print(real_tx.hex())
#
#