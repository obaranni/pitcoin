import struct
import base58

DECIMALS = 8
MAX_AMOUNT = 21000000
# recipient = str(lines[0])
#             amount = float(lines[1])


class Output:
    def __init__(self, address, value, script_type='p2pkh'):
        self.script = b''
        self.address = address
        self.value = struct.pack("<Q", value)
        if script_type == 'p2pkh':
            self.p2pkh_script(address)
        self.script_len = struct.pack("<B", len(self.script))

    def p2pkh_script(self, address):
        recipient_hashed_pubkey = base58.b58decode_check(address)[1:].hex()
        self.script = bytes.fromhex("76a914%s88ac" % recipient_hashed_pubkey)

    def get_raw_format(self):
        return (
            self.value
            + self.script_len
            + self.script
        )


def flip_byte_order(string):
    flipped = "".join(reversed([string[i:i + 2] for i in range(0, len(string), 2)]))
    return flipped