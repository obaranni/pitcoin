import hashlib
import base58
import ecdsa
import struct
from enum import Enum
from ecdsa.util import string_to_number, number_to_string
from ecdsa.curves import SECP256k1

CURVE_ORDER = SECP256k1.order
input_amount = int(0.1516 * 10 ** 8)
output_amount = int(0.1515 * 10 ** 8)
fee = int(0.0001 * 10 ** 8)
sender_address = "mv3d5P4kniPrT5owreux438yEtcFUefo71"
sender_pub = "04C3C6A89E01B4B62621233C8E0C2C26078A2449ABAA837E18F96A1F65D7B8CC8CC5F96F69C917C286BB324A7B400A69ED6FC3CDA20BC292DC9B2414ADD80029D2"
sender_compressed_pub = "02C3C6A89E01B4B62621233C8E0C2C26078A2449ABAA837E18F96A1F65D7B8CC8C"
sender_pub_bytes = bytes.fromhex(sender_pub)
sender_compressed_pub_bytes = bytes.fromhex(sender_compressed_pub)
sender_priv = "884a1c97e9feb617ece801bb13ad7251854f9f0821f2f61237accbe085be58af"
sender_wif_priv = "5JrJuxQ5QhLASMpQgSCZ9Fmzt8Sit8X3h1N9LGWYdXDtBhUxCwB"
recipient_address = "mv3d5P4kniPrT5owreux438yEtcFUefo71"
prev_txid = "2e32e585828d0cd00fdde670fdbd65b7b5d4a12ef7511a3627b59392f46aa2d5"



def flip_byte_order(string):
    flipped = "".join(reversed([string[i:i + 2] for i in range(0, len(string), 2)]))
    return flipped


from sys import byteorder
from hashlib import sha256

## You can put in $data an 80-byte block header to get its header hash,
## or a raw transaction to get its txid
data = "01000000019508af76acc0dde184eee47e4ef861cfe43048c6450674ff3ac93f77445feb5a000000006a47304402205b15c520816d375d15c04ce31d3fdc64c4be8b5a15e5fcd6cd0b701df25a5d1402200495c90edb9070868f6f0f7e257471344c9ad1a5ea84ac0ca32315c44adf17f3012102c3c6a89e01b4b62621233c8e0c2c26078a2449abaa837e18f96a1f65d7b8cc8cffffffff01b02be700000000001976a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac00000000"
hash = sha256(sha256(bytes.fromhex(data)).digest()).digest()

print("Internal-Byte-Order Hash: ", hash.hex())
print("RPC-Byte-Order Hash:      ", hash[::-1].hex())





def ripemd160(x):
    d = hashlib.new('ripemd160')
    d.update(x)
    return d


class Network(Enum):
    TEST_NET = 0
    PROD_NET = 1


class raw_tx:
    version = struct.pack("<L", 1)
    tx_in_count = struct.pack("<B", 1)
    tx_in = {}  # TEMP
    tx_out_count = struct.pack("<B", 2)
    tx_out1 = {}  # TEMP
    tx_out2 = {}  # TEMP
    lock_time = struct.pack("<L", 0)





def normalize_secret_bytes(privkey_bytes: bytes) -> bytes:
    scalar = string_to_number(privkey_bytes) % CURVE_ORDER
    if scalar == 0:
        raise Exception('invalid EC private key scalar: zero')
    privkey_32bytes = number_to_string(scalar, CURVE_ORDER)
    return privkey_32bytes

def make_raw_transaction():
    rtx = raw_tx()

    my_address = sender_address
    my_hashed_pubkey = base58.b58decode_check(my_address)[1:].hex()

    my_private_key = sender_wif_priv
    my_private_key_hex = base58.b58decode_check(my_private_key)[1:33].hex()

    recipient = recipient_address
    recipient_hashed_pubkey = base58.b58decode_check(recipient)[1:].hex()

    my_output_tx = prev_txid
    input_value = input_amount
    # form tx_in
    rtx.tx_in["txouthash"] = bytes.fromhex(flip_byte_order(my_output_tx))
    rtx.tx_in["tx_out_index"] = struct.pack("<L", 1)
    rtx.tx_in["script"] = bytes.fromhex("76a914%s88ac" % my_hashed_pubkey)
    rtx.tx_in["scrip_bytes"] = struct.pack("<B", len(rtx.tx_in["script"]))
    rtx.tx_in["sequence"] = bytes.fromhex("ffffffff")

    # form tx_out
    rtx.tx_out1["value"] = struct.pack("<Q", output_amount)
    rtx.tx_out1["pk_script"] = bytes.fromhex("76a914%s88ac" % recipient_hashed_pubkey)
    rtx.tx_out1["pk_script_bytes"] = struct.pack("<B", len(rtx.tx_out1["pk_script"]))

    return_value = input_value - output_amount - fee # 1000 left as fee
    rtx.tx_out2["value"] = struct.pack("<Q", return_value)
    rtx.tx_out2["pk_script"] = bytes.fromhex("76a914%s88ac" % my_hashed_pubkey)
    rtx.tx_out2["pk_script_bytes"] = struct.pack("<B", len(rtx.tx_out2["pk_script"]))
    # =========================================
    # form raw_tx
    raw_tx_string = (
            rtx.version
            + rtx.tx_in_count
            + rtx.tx_in["txouthash"]
            + rtx.tx_in["tx_out_index"]
            + rtx.tx_in["scrip_bytes"]
            + rtx.tx_in["script"]
            + rtx.tx_in["sequence"]
            + rtx.tx_out_count
            + rtx.tx_out1["value"]
            + rtx.tx_out1["pk_script_bytes"]
            + rtx.tx_out1["pk_script"]
            + rtx.tx_out2["value"]
            + rtx.tx_out2["pk_script_bytes"]
            + rtx.tx_out2["pk_script"]
            + rtx.lock_time
            + struct.pack("<L", 1)
    )

    print(raw_tx_string.hex())

    hashed_tx_to_sign = hashlib.sha256(hashlib.sha256(raw_tx_string).digest()).digest()
    print(hashed_tx_to_sign.hex())

    pk_bytes = bytes.fromhex(my_private_key_hex)
    sk = ecdsa.SigningKey.from_string(pk_bytes, curve=ecdsa.SECP256k1)
    # vk = sk.verifying_key

    # can be used for uncompressed pubkey
    # vk_string = vk.to_string()
    # public_key_bytes = b'\04' + vk_string

    public_key_bytes_hex = sender_compressed_pub
    signature = sk.sign_digest(hashed_tx_to_sign, sigencode=ecdsa.util.sigencode_der_canonize)

    sigscript = (

            signature
            + b'\01'
            + struct.pack("<B", len(bytes.fromhex(public_key_bytes_hex)))
            + bytes.fromhex(public_key_bytes_hex)
    )

    real_tx = (
            rtx.version
            + rtx.tx_in_count
            + rtx.tx_in["txouthash"]
            + rtx.tx_in["tx_out_index"]
            + struct.pack("<B", len(sigscript) + 1)
            + struct.pack("<B", len(signature) + 1)
            + sigscript
            + rtx.tx_in["sequence"]
            + rtx.tx_out_count
            + rtx.tx_out1["value"]
            + rtx.tx_out1["pk_script_bytes"]
            + rtx.tx_out1["pk_script"]
            + rtx.tx_out2["value"]
            + rtx.tx_out2["pk_script_bytes"]
            + rtx.tx_out2["pk_script"]
            + rtx.lock_time

    )
    print("raw_tx " + '=' * 30)
    print(real_tx.hex())


def main():
    make_raw_transaction()
    pass


if __name__ == "__main__":
    main()