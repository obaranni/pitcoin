import cmd
import requests
import json
import os, re
from random import  randint, randrange
import time
from wallet_utils import wallet_utils
from tools.serializer import Serializer
from classes.Transaction import Transaction, BadTransactionFormat
from tools import tx_validator as tx_v

DECIMALS = 8         # create header ???
MAX_AMOUNT = 6553.5  # 6553.5 from max short 65535 / 10

PRIVATE_KEYS = []
ADDRESSES = []
TRANSACTIONS = []

pitcoin_node_ip = 'http://127.0.0.1:5000'
testnet_node_ip = 'https://chain.so/api/v2'
network = 'BTCTEST'


# TODO: to other file

class WrongIp(Exception):
    pass


class WrongLineArgs(Exception):
    pass


class WrongPublicKey(Exception):
    pass


class AmountError(Exception):
    pass


class WrongRecipientAddress(Exception):
    pass


class WrongSenderAddress(Exception):
    pass


class WrongTransactionSignature(Exception):
    pass


class WrongRawTransaction(Exception):
    pass

# class BadInputFormat(Exception):
#     pass

# TODO: to other file

CRED = '\033[91m'
CGREEN = '\033[92m'
CEND = '\033[0m'

# send {"inputs": [{"tx_id": "f904ba9b44ae2b68d5663289b52545fdab9c4a9d9a855fe05ab1e8a3cee56814", "tx_out_id": "0", "tx_script": "76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac", "value": "0.00009"}, {"tx_id": "0bcedf6c019a14e7a187b08279f203098a42d336097e372129aad14432b4e768", "tx_out_id": "0", "tx_script": "76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac", "value": "0.0002"}]} {"outputs": [{"address": "mv3d5P4kniPrT5owreux438yEtcFUefo71", "value": "0.00009", "script_type": "p2pkh"},{"address": "mv3d5P4kniPrT5owreux438yEtcFUefo71", "value": "0.00009", "script_type": "p2pkh"},{"address": "mv3d5P4kniPrT5owreux438yEtcFUefo71", "value": "0.00009", "script_type": "p2pkh"}]}

# send {"inputs": [{"tx_id": "a7ab8310eb40ff4c4c53814cd2727c64b9d7835dfa82d0f8d14797140062babf", "tx_out_id": "20", "tx_script": "76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac", "value": "0.15262973"}, {"tx_id": "96cf299755eeb25368b02682781be74845679b77bdd575487cf1d35cfbedf3da", "tx_out_id": "1", "tx_script": "76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac", "value": "0.00001"}, {"tx_id": "96cf299755eeb25368b02682781be74845679b77bdd575487cf1d35cfbedf3da", "tx_out_id": "2", "tx_script": "76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac", "value": "0.00001"}, {"tx_id": "f0ffffb5b35f45b4c4d8f013935d1b275cd56da15872e610407c8a3dc414a16e", "tx_out_id": "0", "tx_script": "76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac", "value": "0.00014999"}]} {"outputs": [{"address": "mv3d5P4kniPrT5owreux438yEtcFUefo71", "value": "0.152", "script_type": "p2pkh"}]}

# send {"inputs": [{"tx_id": "18776aab24657972ae8fcbb3b2b26a48cd50b55ad47a36af1e60881cf0cac5d8", "tx_out_id": "0", "tx_script": "76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac", "value": "0.1519"}]} {"outputs": [{"address": "mv3d5P4kniPrT5owreux438yEtcFUefo71", "value": "0.1518", "script_type": "p2pkh"}]}

# send {"inputs": [ {"tx_id": "226c435ab0b3bb1d84d2bb001dc71a980687329deb5216836ba465d37cc6279d", "tx_out_id": "0", "tx_script": "76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac", "value": "0.1517"} ]} {"outputs": [{"address": "mv3d5P4kniPrT5owreux438yEtcFUefo71", "value": "0.1516", "script_type": "p2pkh"}]}


status_codes = {
    "Transaction pull i empty": 101,
    "Node added": 102,
    "Cannot start mine mode": 103,
    "Transaction pended": 201,
    "Bad json format": 401,
    "Bad transaction": 402,
}


class WalletCli(cmd.Cmd):
    intro = "\n\n   Welcome to the wallet command line interface!\n" \
            "   Enter \"help\" to get the list of commands.\n   Enter" \
            " \"exit\" to exit\n\n"
    prompt = "wallet_cli: "

    def help_wif(self):
        print("\nwif help:\nConverts private key to wif format\nSpecify the correct private key\n")

    def help_import(self):
        print("\nimport help:\nConverts from WIF format to simple privat key\n"
              "Specify the path to the file\nFor example: \"import storage/wifKey\"\n")

    def help_new(self):
        print("\nnew help:\nCreates a new key pair\n")

    def help_help(self):
        print("\nhelp help:\nList available commands with \"help\" or detailed help with \"help *command_name*\".\n")
        return True

    def help_endpoin(self):
        print("\nendpoint help:\nChange node\nExample: \"endpoint 127.0.0.1:5000\"\n")

    def help_send(self):
        print("\nsend help:\nSends transaction\nExample:\n"
              "Raw: {\"inputs\": [{\"tx_id\": \"**ID**\", \"tx_out_id\": \"**OUT_ID**\", \"tx_script\": \"**SCRIPT**\", \"value\": \"12345678\"}, {\"tx_id\": \"**ID**\", \"tx_out_id\": \"**OUT_ID**\", \"tx_script\": \"**SCRIPT**\", \"value\": \"12345678\"}]}\n"
              "Raw: {\"outputs\": [{\"address\": \"**ADDRESS**\", \"value\": \"**VALUE**\", \"script_type\": \"p2pkh\"}, {\"address\": \"**ADDRESS**\", \"value\": \"**VALUE**\", \"script_type\": \"p2pkh\"}]}\n")

    def help_cmdimport(self):
        print("\nhelp cmdimport:\ncmdimport imports private key from command line \"cmdimport *private_key*\".\n")


    def emptyline(self):
        self.do_help(0)

    def do_exit(self, line):
        return True

    def do_random(self, line):

        private_key, public_key, address = wallet_utils.newKeyPair()
        i = 0
        if len(line) == 0:
            line = "200"
        while i < int(line):
            amount = randrange(0, 65535)
            private_key2, public_key2, address2 = wallet_utils.newKeyPair()
            PRIVATE_KEYS.append(private_key)
            pitoshi = "{0:0{1}x}".format(amount, 4)
            tx = Transaction(address, address2,
                         bytes(pitoshi.encode('utf-8')).decode('utf-8'))
            tx.calculate_hash()
            signature, verify_key = wallet_utils.signMessage(private_key, tx.get_hash())
            tx.set_sign(signature, verify_key)
            secs = randint(0, 3)
            time.sleep(secs)
            ser_tx = Serializer(tx).get_serialized_tx()
            TRANSACTIONS.append(ser_tx)
            self.do_broadcast(line)
            i += 1

    def do_new(self, line):
        private_key, public_key, address = wallet_utils.newKeyPair()
        PRIVATE_KEYS.append(private_key)
        ADDRESSES.append(address)
        wallet_utils.saveKeyToFile(address)
        print_keys_info(private_key)

    def do_cmdimport(self, line): # TODO: should be validation
        if len(line) < 64:
            print("Wrong key format")
            self.help_cmdimport()
            return False
        PRIVATE_KEYS.append(line)
        public_key = wallet_utils.fullSettlementPublicAddress(line)
        ADDRESSES.append(public_key)
        wallet_utils.saveKeyToFile(public_key)
        print_keys_info(line)

    def do_wif(self, line):  # TODO: should be validation
        if len(line) < 64:
            print("Wrong key format")
            self.help_wif()
            return False
        print("WIF private key: %s" % wallet_utils.privateKeyToWIF(line).decode('utf-8'))

    def do_import(self, line): # TODO: should be validation
        if line == '':
            self.help_import()
            return False
        key = wallet_utils.readKeyFromFile(line)
        if key is None:
            return False
        decoded_key = wallet_utils.wifKeyToPrivateKey(key)
        if decoded_key is None:
            return False
        PRIVATE_KEYS.append(decoded_key)
        public_key = wallet_utils.fullSettlementPublicAddress(decoded_key)
        ADDRESSES.append(public_key)
        wallet_utils.saveKeyToFile(public_key)
        print_keys_info(decoded_key)

    def do_getmyutxos(self, line):
        try:
            if len(line) > 1 and line.find("-t") != -1:
                endpoint = testnet_node_ip + '/get_tx_unspent/' + network + '/' + ADDRESSES[-1]
                resp = requests.get(url=endpoint)
                content = resp.json()
                print("outs:", len(content['data']['txs']))
                amount = 0.0
                for i in content['data']['txs']:
                    amount += float(i['value'])
                print("amount:", amount)
                print(json.dumps(content['data']['txs'], indent=4))
            else:
                print("MY UTXOS")
        except IndexError:
            print("Generate or import private key first")
            return False

    def do_broadcast(self, line):
        global pitcoin_node_ip

        try:
            if len(line) > 1 and line.find("-t") != -1:
                endpoint = testnet_node_ip + '/send_tx/' + network
                print(endpoint)
                params = (('tx_hex', TRANSACTIONS[-1]),)
                resp = requests.post(url=endpoint, params=params)
                content = resp.json()
                print(CGREEN, content)
                code = 201
            else:
                url = pitcoin_node_ip + '/transaction/new'
                print(url)
                post_data = {'serialized_tx': str(TRANSACTIONS[-1])}
                resp = requests.post(url=url, json=post_data)
                code = resp.status_code
        except:
            print(CRED, end="")
            print("[from: cli]: cannot send request", CEND)
            return False
        if code < 300:
            print(CGREEN, end="")
        for i in status_codes:
            if status_codes[i] == code:
                print("[from: node]:", i)
        print(CEND, end="")

    def do_send(self, line):
        try:
            sender_private = PRIVATE_KEYS[-1]
            lines = str(line).split(']}')              # TODO: better split
            if len(lines) != 3 or len(lines[2]) > 1 :
                raise WrongLineArgs
            tx = Transaction(lines[0] + ']}', lines[1] + ']}')
            tx.get_presign_raw_format()
            tx.calculate_hash()
            sender_pub_key = wallet_utils.getPublickKey(sender_private)
            sender_compressed_pub_key = wallet_utils.compressPublicKey(sender_pub_key)
            tx.sign_tx(sender_private)
            ser_tx = tx.get_signed_raw_format(sender_compressed_pub_key).hex()
            TRANSACTIONS.append(ser_tx)
            print(ser_tx)
        except BadTransactionFormat:
            print("Cannot create transaction")
            return False
        except IndexError:
            print("Generate or import private key first")
            return False

    def do_endpoint(self, line):
        if len(line) < 1:
            self.help_endpoin()
            return False
        try:
            global pitcoin_node_ip

            line = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}\b", line)
            if len(line) < 1:
                raise WrongIp

            pitcoin_node_ip = 'http://' + line[0]
            url = pitcoin_node_ip + '/chain/length'
            requests.post(url=url, json='')
            print(CGREEN, "[from: cli]: connected", CEND, sep="")
        except WrongIp:
            print(CRED, "[from: cli]: wrong node ip", CEND, sep="")
            self.help_endpoin()
        except requests.exceptions.ConnectionError:
            print(CRED, "[from: cli]: cannot connect", CEND, sep="")

    def do_deserialize(self, line):
        if len(line) < 50:
            print("Too short tx")
            return False
        tx = Transaction(False, False)
        tx.set_signed_raw_tx(line)
        tx.deserialize_raw_tx()

def print_keys_info(private_key):
    print("Private key: \"", private_key, "\"", sep="")
    print("Look for your public key at storage/address.txt line %d" % int(wallet_utils.getFileLines()))


if __name__ == '__main__':
    WalletCli().cmdloop()


# import storage/wifKey











"""

old:
version :        01000000
tx_in_counts:    01
Prev_hash:          1ba58ce93e5a6e31f281f50e21881d6fce206003dc008c73ff6e273b56073403
tx_out_index:       01000000
script_len:         6a
script:                 47
                            30440220457d6125e0565a28add15b0cc19664fbdadd6161c368e3407cf6c2a4ab9e16f302207eb743c3f67f07a3657388704144930172f625c6fe4e410d32210853af22805801
                        21
                            02c3c6a89e01b4b62621233c8e0c2c26078a2449abaa837e18f96a1f65d7b8cc8c 
seq:                ffffffff
    
    02204e0000000000001976a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac204e0000000000001976a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac00000000

new:
                01000000
                02
                    68e7b43244d1aa2921377e0936d3428a0903f27982b087a1e7149a016cdfce0b
                    00000000
                    6b
                        48
                            3045022100fc4c73adfdd65d4879ee477e8d800172d49f6be957c4ef45e25cf2520e38e62202203565827c645c934b5786a25e27bce1b8bae48a54f66489587c669ed9b74732e501
                        21
                            02c3c6a89e01b4b62621233c8e0c2c26078a2449abaa837e18f96a1f65d7b8cc8c
                    ffffffff
                    68e7b43244d1aa2921377e0936d3428a0903f27982b087a1e7149a016cdfce0b
                    
                    01000000
                    6b
                        48
                            3045022100fc4c73adfdd65d4879ee477e8d800172d49f6be957c4ef45e25cf2520e38e62202203565827c645c934b5786a25e27bce1b8bae48a54f66489587c669ed9b74732e501
                        21
                            02c3c6a89e01b4b62621233c8e0c2c26078a2449abaa837e18f96a1f65d7b8cc8c
                    ffffffff
                    
                    
                04
                    2823000000000000
                    19
                        76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac
                    
                    2823000000000000
                    19
                        76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac
                        
                    2823000000000000
                    19
                        76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac
                        
                    2823000000000000
                    19
                        76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac
                    
                    00000000
                    
                    
                
                
46
    304302206fe3ab3c66460619034c1f8008d5d7df132a98f76916e8ba35562bb7cb937c41021f2ee468f7857cd3c7681d02f60e270782cf3c832342e2f2ad266e8ddf7f4d1f01
21
    02c3c6a89e01b4b62621233c8e0c2c26078a2449abaa837e18f96a1f65d7b8cc8c     
                    
                    
                    
68e7b43244d1aa2921377e0936d3428a0903f27982b087a1e7149a016cdfce0b
00000000
6b
    48
        3045022100fc886a2462442e00920b5292fca4ec3b92bc070ef727207c4f8844c0aa025d2e0220539daf12033ed2d214b893c3e8139dfeaa627c32fca6eba076ec2d991e3e7c7101
    21
        02c3c6a89e01b4b62621233c8e0c2c26078a2449abaa837e18f96a1f65d7b8cc8c
    ffffffff
"""



