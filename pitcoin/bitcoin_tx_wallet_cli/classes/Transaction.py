import hashlib, base58, ecdsa, json, struct, sys, os
from enum import Enum
from ecdsa.util import string_to_number, number_to_string
from ecdsa.curves import SECP256k1
from .Input import Input
from .Output import Output
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))
import tx_validator

CURVE_ORDER = SECP256k1.order

DECIMALS = 8
MAX_AMOUNT = 21000000
ADDRESS_LEN = 35

class BadOutIndex(Exception):
    pass

class BadHash(Exception):
    pass

class BadAddress(Exception):
    pass

class BadInputFormat(Exception):
    pass

class BadAmount(Exception):
    pass

class BadTransactionFormat(Exception):
    pass

class BadOutputFormat(Exception):
    pass

class BadOutputData(Exception):
    pass

class BadInputData(Exception):
    pass

# TODO:                check input_values - output_values >= 0

class Transaction:
    def __init__(self, inputs, outputs, version=1, locktime=0):
        try:
            self.version = struct.pack("<L", version)
            self.numb_inputs = struct.pack("<B", 0)
            self.numb_outputs = struct.pack("<B", 0)
            self.inputs = []
            self.outputs = []
            if inputs and outputs:
                self.create_inputs(inputs)
                self.create_outputs(outputs)
            self.locktime = struct.pack("<L", locktime)
            self.raw_tx = []
            self.real_raw_tx = None
            self.tx_hashes = []
            self.signs = []
        except BadInputFormat:
            print("Cannot create input")
            raise BadTransactionFormat
        except BadOutputFormat:
            print("Cannot create output")
            raise BadTransactionFormat

    def validate_input(self, input):
        try:
            int(input['tx_id'], 16)
            if len(input['tx_id']) != 64:
                raise BadHash
            if int(input['tx_out_id']) < 0 or int(input['tx_out_id']) > 200:
                raise BadOutIndex
            # TODO: validate script
            amount = float(input['value'])
            if float(amount) > MAX_AMOUNT or len(str(amount).split('.')[1]) > DECIMALS:
                raise BadAmount
            return True
        except BadAmount:
            print("Bad amount!")
        except BadOutIndex:
            print("Bad tx_out_id!")
        except ValueError:
            print("Bad tx_id symbols!")
        except BadHash:
            print("Bad tx_id len!")
        except:
            print("Bad json format!")
        raise BadInputData

    def create_inputs(self, inputs):
        try:
            inputs_dict = json.loads(inputs)['inputs']
            inputs_arr = [i for i in inputs_dict]
            for i in inputs_arr:
                self.validate_input(i)
                self.inputs.append(Input(i['tx_id'], i['tx_out_id'], i['tx_script']))
            self.numb_inputs = struct.pack("<B", len(self.inputs))
        except BadInputData:
            print("Bad inputs data")
            raise BadInputFormat
        except:
            print("Bad inputs json format")
            raise BadInputFormat

    def validate_output(self, output):
        try:
            amount = output['value']
            if float(amount) > MAX_AMOUNT or len(str(amount).split('.')[1]) > DECIMALS:
                raise BadAmount
            output['value'] = int(float(amount) * int(pow(10, DECIMALS)))
            if not tx_validator.validate_address(output['address']):
                raise BadAddress
            return True
        except BadAddress:
            print("Bad address!")
        except BadAmount:
            print("Bad amount!")
        raise BadOutputData

    def create_outputs(self, outputs):
        try:
            outputs_dict = json.loads(outputs)['outputs']
            outputs_arr = [i for i in outputs_dict]
            for i in outputs_arr:
                self.validate_output(i)
                self.outputs.append(Output(i['address'], i['value'], i['script_type']))
            self.numb_outputs = struct.pack("<B", len(self.outputs))
        except BadOutputData:
            print("Bad outputs data")
            raise BadOutputFormat
        except:
            print("Bad outputs json format")
            raise BadOutputFormat

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

    def set_signed_raw_tx(self, raw_tx):
        self.real_raw_tx = raw_tx

    def deserialize_raw_tx(self):
        start_point = 0
        end_point = 8
        version = struct.unpack("<L", bytes.fromhex(self.real_raw_tx[start_point:end_point]))[0]
        start_point = end_point
        end_point += 2
        numb_inputs = struct.unpack("<B", bytes.fromhex(self.real_raw_tx[start_point:end_point]))[0]

        print("\nversion", version)
        print("numb_inputs", numb_inputs)

        for i in range(0, numb_inputs):
            start_point = end_point
            end_point += 64
            prev_tx_id = flip_byte_order(self.real_raw_tx[start_point:end_point])
            start_point = end_point
            end_point += 8
            out_index = struct.unpack("<L", bytes.fromhex(self.real_raw_tx[start_point:end_point]))[0]
            start_point = end_point
            end_point += 2
            script_len = struct.unpack("<B", bytes.fromhex(self.real_raw_tx[start_point:end_point]))[0] * 2
            start_point = end_point
            end_point += script_len
            script = self.real_raw_tx[start_point:end_point]
            start_point = end_point
            end_point += 8
            sequence = self.real_raw_tx[start_point:end_point]
            print("\nprev_tx_id", prev_tx_id)
            print("out_index", out_index)
            print("script_len", script_len, "in bytes", int(script_len / 2))
            print("script", script)
            print("sequence", sequence)

        start_point = end_point
        end_point += 2
        numb_outputs = struct.unpack("<B", bytes.fromhex(self.real_raw_tx[start_point:end_point]))[0]

        print("\nnumb_outputs", numb_outputs)


        for i in range(0, numb_outputs):
            start_point = end_point
            end_point += 16
            amount = struct.unpack("<Q", bytes.fromhex(self.real_raw_tx[start_point:end_point]))[0] / 100000000
            start_point = end_point
            end_point += 2
            script_len = struct.unpack("<B", bytes.fromhex(self.real_raw_tx[start_point:end_point]))[0] * 2
            start_point = end_point
            end_point += script_len
            script = self.real_raw_tx[start_point:end_point]

            print("\namount", amount)
            print("script_len", script_len, "in bytes", int(script_len / 2))
            print("script", script)



        start_point = end_point
        end_point += 8
        locktime = struct.unpack("<L", bytes.fromhex(self.real_raw_tx[start_point:end_point]))[0]
        print("\nlocktime", locktime, end="\n\n")


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
