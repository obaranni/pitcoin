import struct


DECIMALS = 8
MAX_AMOUNT = 21000000
# recipient = str(lines[0])
#             amount = float(lines[1])


class Output:
    def __init__(self, address, value, script_type):
        self.script = b''
        self.address = address
        self.value = struct.pack("<Q", value)
        if script_type == 'p2phk':
            self.p2pkh_script(address)
        self.script_len = struct.pack("<B", len(self.script))

    def p2pkh_script(self, address):
        self.script = bytes.fromhex("76a914%s88ac" % address)

    def get_raw_format(self):
        return (
            self.value
            + self.script_len
            + self.script
        )


def flip_byte_order(string):
    flipped = "".join(reversed([string[i:i + 2] for i in range(0, len(string), 2)]))
    return flipped