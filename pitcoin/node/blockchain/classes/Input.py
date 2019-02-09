import struct

class Input:
    def __init__(self, input_tx_id, out_index, out_script, sequence="ffffffff", script_type="p2pkh"):
        print(out_script)
        self.input_tx_id = bytes.fromhex(flip_byte_order(input_tx_id))
        self.out_index = struct.pack("<L", int(out_index))
        self.out_script = bytes.fromhex(out_script)
        self.out_script_len = struct.pack("<B", len(self.out_script))
        self.out_zero_script = bytes.fromhex("")
        self.out_zero_script_len = struct.pack("<B", len(self.out_zero_script))
        self.sequence = bytes.fromhex(sequence)
        self.script_type = script_type
        self.unlock_script = None
        self.sign = None

    def get_presign_raw_format(self):
        return (
            self.input_tx_id
            + self.out_index
            + self.out_script_len
            + self.out_script
            + self.sequence
        )

    def get_presign_zero_script_raw_format(self):
        return (
            self.input_tx_id
            + self.out_index
            + self.out_zero_script_len
            + self.out_zero_script
            + self.sequence
        )

    def p2pkh_unlock_script(self, sign, compressed_pub):
        self.sign = sign
        self.unlock_script = (
                sign
                + b'\01'
                + struct.pack("<B", len(bytes.fromhex(compressed_pub.decode('utf-8'))))
                + bytes.fromhex(compressed_pub.decode('utf-8'))
        )
        return self.unlock_script

    def create_unlock_script(self, sign, compressed_pub):
        if self.script_type == 'p2pkh':
            self.p2pkh_unlock_script(sign, compressed_pub)

    def get_sign_raw_format(self, sign, compressed_pub_key):
        self.create_unlock_script(sign, compressed_pub_key)
        return (
            self.input_tx_id
            + self.out_index
            + struct.pack("<B", len(self.unlock_script) + 1)
            + struct.pack("<B", len(self.sign) + 1)
            + self.unlock_script
            + self.sequence
        )

def flip_byte_order(string):
    flipped = "".join(reversed([string[i:i + 2] for i in range(0, len(string), 2)]))
    return flipped