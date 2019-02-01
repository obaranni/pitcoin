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


import struct
import base58
import codecs
import hashlib

amount1 = 100000
amount2 = 800000
sender_address = "mqGwEkV6negvHgoi3km632M16Qfqo8YGkS"
sender_pub = "0458DED3507BDD1A45C46A746265075081768653FA2C455C9A8AEEEAFCC47C235DA97750E8FF8AF18FC683FA0BE5D178F3369C1717174D90525125066AE68A5746"
sender_pub_bytes = bytes.fromhex(sender_pub)
sender_priv = "099593d07216431aa4a2e7855cfdb74f5e9ea397d8614d38fa92ef1fad348dee"
recipient_address = "n3Jqa2cyGqKDvc8QNMKYooy5yYUqoGwrvi"
prev_txid = "cad518e8481c1990e9a88f64cf85942e3b2bce279ab3fde447efa3d019a1b098"

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
# print(recipient_hashed_pub_key)
tx = NewTransaction()
tx.tx_in['tx_out_hash'] = bytes.fromhex(revert_bytes(prev_txid))
tx.tx_in['tx_out_index'] = struct.pack("<L", 1)
tx.tx_in['script'] = bytes.fromhex(sender_pub)
tx.tx_in['script_bytes'] = struct.pack("<B", len(tx.tx_in['script']))
tx.tx_in['sequence'] = bytes.fromhex("ffffffff")

tx.tx_out1['amount'] = struct.pack("<Q", amount1)
tx.tx_out1['pk_script'] = bytes.fromhex("76a914%s88ac" % recipient_hashed_pub_key)
tx.tx_out1['pk_script_bytes'] = struct.pack("<B", len(tx.tx_out1['pk_script']))

tx.tx_out2['amount'] = struct.pack("<Q", amount2)
tx.tx_out2['pk_script'] = bytes.fromhex("76a914%s88ac" % sender_hashed_pub_key)
tx.tx_out2['pk_script_bytes'] = struct.pack("<B", len(tx.tx_out2['pk_script']))

# print(tx.version, type(tx.version))
# print(tx.tx_in_count, type(tx.tx_in_count))
# print(tx.tx_out_count, type(tx.tx_out_count))
# print(tx.tx_in['tx_out_hash'], type(tx.tx_in['tx_out_hash']))
# print(tx.tx_in['tx_out_index'], type(tx.tx_in['tx_out_index']))
# print(tx.tx_in['script'], type(tx.tx_in['script']))
print(tx.tx_in['script_bytes'], type(tx.tx_in['script_bytes']))
# print(tx.tx_in['sequence'], type(tx.tx_in['sequence']))
#
# print(tx.tx_out1['amount'], type(tx.tx_out1['amount']))
# print(tx.tx_out1['pk_script'], type(tx.tx_out1['pk_script']))
# print(tx.tx_out1['pk_script_bytes'], type(tx.tx_out1['pk_script_bytes']))
#
# print(tx.tx_out2['amount'], type(tx.tx_out2['amount']))
# print(tx.tx_out2['pk_script'], type(tx.tx_out2['pk_script']))
# print(tx.tx_out2['pk_script_bytes'], type(tx.tx_out2['pk_script_bytes']))

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

sign_script = (
    struct.pack("<B", len(sign))
    + sign
    + struct.pack("<B", len(sender_pub_bytes))
    + sender_pub_bytes
)


real_tx = (
    tx.version
    + tx.tx_in_count
    + tx.tx_in['tx_out_hash']
    + tx.tx_in['tx_out_index']
    + struct.pack("<B", len(sign + sender_pub_bytes) + 2)
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
# 9faed6e321e5087340080eee3b09702ecef858caaf4fa03c1ff3f0661702cefcdeb3439537b23481f113158c97fe8b39ded868df096b9bb89936eb61e3cbb78a01
# 4bb51ba545d5e5adfd7d7e4fa01ff9b8a67fb971b4b3729655eb14c849da9d5d97bbfe0fb8ba508e67fdc0b6f19fe3988989e1cf91d1ea3b63d1c2123083892142