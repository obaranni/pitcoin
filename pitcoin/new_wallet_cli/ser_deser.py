import cmd
import requests
import json
import os, re
from random import  randint, randrange
import time
from wallet_utils import wallet_utils
from tools.serializer import Serializer
from classes.transaction import Transaction
from tools import tx_validator as tx_v

from cryptos import *

import struct
import base58
import codecs
import hashlib

amount1 = 100000
amount2 = 800000
sender_address = "mv3d5P4kniPrT5owreux438yEtcFUefo71"
sender_pub = "04C3C6A89E01B4B62621233C8E0C2C26078A2449ABAA837E18F96A1F65D7B8CC8CC5F96F69C917C286BB324A7B400A69ED6FC3CDA20BC292DC9B2414ADD80029D2"
sender_compressed_pub = "02C3C6A89E01B4B62621233C8E0C2C26078A2449ABAA837E18F96A1F65D7B8CC8C"
sender_pub_bytes = bytes.fromhex(sender_pub)
sender_compressed_pub_bytes = bytes.fromhex(sender_compressed_pub)
sender_priv = "884a1c97e9feb617ece801bb13ad7251854f9f0821f2f61237accbe085be58af"
recipient_address = "n3Jqa2cyGqKDvc8QNMKYooy5yYUqoGwrvi"
prev_txid = "5ce1d940cefd4e1faf49b4581d33ac8f8dfa54b5b506333291a5ddcb2396aab4"


def revert_bytes(data_str):
    reversed_data = "".join(reversed([data_str[i:i+2] for i in range(0, len(data_str), 2)]))
    return reversed_data


class NewTransaction:
    version = struct.pack("<L", 1)
    tx_in_count = struct.pack("<B", 1)
    tx_in = {}
    tx_out_count = struct.pack("<B", 2)
    tx_out1 = {}
    tx_out2 = {}
    lock_time = struct.pack("<L", 0)

    def __init__(self):
        pass


recipient_hashed_pub_key = codecs.encode(base58.b58decode_check(recipient_address)[1:], "hex").decode('utf-8')
sender_hashed_pub_key = codecs.encode(base58.b58decode_check(sender_address)[1:], "hex").decode('utf-8')


tx = NewTransaction()
tx.tx_in['tx_out_hash'] = bytes.fromhex(revert_bytes(prev_txid))
tx.tx_in['tx_out_index'] = struct.pack("<L", 1)
tx.tx_in['script'] = bytes.fromhex("76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac")
tx.tx_in['script_bytes'] = struct.pack("<B", len(tx.tx_in['script']))
tx.tx_in['sequence'] = bytes.fromhex("ffffffff")

tx.tx_out1['amount'] = struct.pack("<Q", amount1)
tx.tx_out1['pk_script'] = bytes.fromhex("76a914%s88ac" % recipient_hashed_pub_key)
tx.tx_out1['pk_script_bytes'] = struct.pack("<B", len(tx.tx_out1['pk_script']))

tx.tx_out2['amount'] = struct.pack("<Q", amount2)
tx.tx_out2['pk_script'] = bytes.fromhex("76a914%s88ac" % sender_hashed_pub_key)
tx.tx_out2['pk_script_bytes'] = struct.pack("<B", len(tx.tx_out2['pk_script']))

raw_tx = (
    tx.version
    + tx.tx_in_count
    + tx.tx_in['tx_out_hash']
    + tx.tx_in['tx_out_index']
    + tx.tx_in['script_bytes']
    + tx.tx_in['script']
    + tx.tx_in['sequence']
    + tx.tx_out_count
    + tx.tx_out1['amount']
    + tx.tx_out1['pk_script_bytes']
    + tx.tx_out1['pk_script']
    + tx.tx_out2['amount']
    + tx.tx_out2['pk_script_bytes']
    + tx.tx_out2['pk_script']
    + tx.lock_time
    + struct.pack("<L", 1)
)


print(raw_tx, type(raw_tx))
hashed_tx = hashlib.sha256(hashlib.sha256(raw_tx).digest()).hexdigest()
print(hashed_tx, type(hashed_tx))
sign, ver_key = wallet_utils.signMessage(sender_priv, hashed_tx)
print(sign)

# sign_script = (
#     sign
#     + struct.pack("<L", 1)
#     + struct.pack("<B", len(sender_pub))
# )

# real_tx = (
#     tx.version
#     + tx.tx_in_count
#     + tx.tx_in['tx_out_hash']
#     + tx.tx_in['tx_out_index']
#     + struct.pack("<B", len(sign_script) + 1)
#     + struct.pack("<B", len(sign) + 1)
#     + sign_script
#     + tx.tx_in['sequence']
#     + tx.tx_out_count
#     + tx.tx_out1['amount']
#     + tx.tx_out1['pk_script_bytes']
#     + tx.tx_out1['pk_script']
#     + tx.tx_out2['amount']
#     + tx.tx_out2['pk_script_bytes']
#     + tx.tx_out2['pk_script']
#     + tx.lock_time
#
# )

# print("asdf", sender_hashed_pub_key)
# print(sender_hashed_pub_key_bytes)
print("123", sign, '\n\n')

sign_script = (
    struct.pack("<B", len(sign) + 1)
    + sign
    + b'\01'
    + struct.pack("<B", len(sender_compressed_pub_bytes))
    + sender_compressed_pub_bytes
)
print(sender_pub, sender_pub_bytes, sender_compressed_pub_bytes)
print("\n\nscript", sign_script)

real_tx = (
    tx.version
    + tx.tx_in_count
    + tx.tx_in['tx_out_hash']
    + tx.tx_in['tx_out_index']
    + struct.pack("<B", len(sign_script))
    + sign_script
    + tx.tx_in['sequence']
    + tx.tx_out_count
    + tx.tx_out1['amount']
    + tx.tx_out1['pk_script_bytes']
    + tx.tx_out1['pk_script']
    + tx.tx_out2['amount']
    + tx.tx_out2['pk_script_bytes']
    + tx.tx_out2['pk_script']
    + tx.lock_time
)



print(real_tx)
print(real_tx.hex())

print(sign.hex(), sender_pub)

# from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
# import logging
#
# rpc_user = "bitcoinrpc"
# rpc_password = "12345678"
#
# logging.basicConfig()
# logging.getLogger("BitcoinRPC").setLevel(logging.DEBUG)
#
# rpc_connection = AuthServiceProxy("http://%s:%s@178.158.203.251:1489"%(rpc_user, rpc_password))
# print(rpc_connection.getinfo())






# print(base58.b58decode("mv3d5P4kniPrT5owreux438yEtcFUefo71").hex())

to_hash_160 = "02C3C6A89E01B4B62621233C8E0C2C26078A2449ABAA837E18F96A1F65D7B8CC8C"

sha = hashlib.new('sha256', codecs.encode(bytes.fromhex(to_hash_160), 'hex')).digest()
sha_str = hashlib.new('sha256', codecs.encode(bytes.fromhex(to_hash_160), 'hex')).hexdigest()
# sha2 = hashlib.new('sha256', codecs.encode(sha, 'hex')).digest()

ripemd = hashlib.new('ripemd160', codecs.encode(sha, 'hex')).digest()
ripemd_str = hashlib.new('ripemd160', codecs.encode(sha, 'hex')).hexdigest()
print("shastr", sha_str)
print("ripemd", ripemd_str)



c = Bitcoin(testnet=True)
priv = sender_priv
pub = c.privtopub(priv)
addr = c.pubtoaddr(pub)
# print(priv, pub, addr)
inputs = [{'output': '5ce1d940cefd4e1faf49b4581d33ac8f8dfa54b5b506333291a5ddcb2396aab4:1', 'value': 1000000}]
outs = [{'value': 100000, 'address': 'n3Jqa2cyGqKDvc8QNMKYooy5yYUqoGwrvi'}, {'value': 800000, 'address': 'mv3d5P4kniPrT5owreux438yEtcFUefo71'}]
tx = c.mktx(inputs, outs)
# print(tx)
tx2 = c.sign(tx, 0, priv)
print(tx2)
# tx3 = c.sign(tx2, 1, priv)
# print(tx3)

tx3 = tx2

# tx4 = c.serialize(tx3)
#
# print(tx4)

# result script 483045022100f3f896e623ddd39a91d74c9b754be21f9a85e5beb55f4edf83b0ba2ec312abfc02207c4dc2d42858eacebb1a1b587c63357ffbc6df606f6491a3afd7a9e2eff3c785014104c3c6a89e01b4b62621233c8e0c2c26078a2449abaa837e18f96a1f65d7b8cc8cc5f96f69c917c286bb324a7b400a69ed6fc3cda20bc292dc9b2414add80029d2









# class WalletCli(cmd.Cmd):
#     intro = "\n\n   Welcome to the serializer!\n" \
#             "   Enter \"help\" to get the list of commands.\n   Enter" \
#             " \"exit\" to exit\n\n"
#     prompt = "serializer: "
#
#     def do_exit(self, line):
#         return True
#
#     def do_deserialize(self, line):
#         # if len(line) == 0:
#         #     print("zlp")
#         #     return False
#         # deserialize(line)
#         tx = NewTransaction()
#         print(tx.version,  tx.tx_out_count)
#
#
#
#
#
# if __name__ == '__main__':
#     WalletCli().cmdloop() 419faed6e321e5087340080eee3b09702ecef858caaf4fa03c1ff3f0661702cefcdeb3439537b23481f113158c97fe8b39ded868df096b9bb89936eb61e3cbb78a0100000082
# 9faed6e321e5087340080eee3b09702ecef858caaf4fa03c1ff3f0661702cefcdeb3439537b23481f113158c97fe8b39ded868df096b9bb89936eb61e3cbb78a01 9f5e9ced489eb7ed8157b533e4199aad1a9b50b2
# 4bb51ba545d5e5adfd7d7e4fa01ff9b8a67fb971b4b3729655eb14c849da9d5d97bbfe0fb8ba508e67fdc0b6f19fe3988989e1cf91d1ea3b63d1c2123083892142
# af137f8ac5782bf522550e005aa21b7fc70b953a7248be309ff279d5175340651da20687b7d9478a68d15bbd465a79297ac68f45f9ed60acfd80ad924a74b3ed 02c3c6a89e01b4b62621233c8e0c2c26078a2449abaa837e18f96a1f65d7b8cc8c