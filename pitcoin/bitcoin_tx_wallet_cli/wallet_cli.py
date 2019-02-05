import cmd
import requests
import json
import os, re
from random import  randint, randrange
import time
from wallet_utils import wallet_utils
from tools.serializer import Serializer
from classes.Transaction import Transaction
from tools import tx_validator as tx_v

DECIMALS = 8         # create header ???
MAX_AMOUNT = 6553.5  # 6553.5 from max short 65535 / 10

PRIVATE_KEYS = []
TRANSACTIONS = []

node_ip = 'http://127.0.0.1:5000'


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

# TODO: to other file

CRED = '\033[91m'
CGREEN = '\033[92m'
CEND = '\033[0m'

# send {"inputs": [{"tx_id": "033407563b276eff738c00dc036020ce6f1d88210ef581f2316e5a3ee98ca51b", "tx_out_id": "1", "tx_script": "76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288ac", "value": "0.0005"}]} {"outputs": [{"address": "mv3d5P4kniPrT5owreux438yEtcFUefo71", "value": "0.0002", "script_type": "p2pkh"}, {"address": "mv3d5P4kniPrT5owreux438yEtcFUefo71", "value": "0.0002", "script_type": "p2pkh"}]}

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
        wallet_utils.saveKeyToFile(address)
        print_keys_info(private_key)

    def do_cmdimport(self, line): # TODO: should be validation
        if len(line) < 64:
            print("Wrong key format")
            self.help_wif()
            return False
        PRIVATE_KEYS.append(line)
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
        wallet_utils.saveKeyToFile(public_key)
        print_keys_info(decoded_key)

    def do_getmyutxos(self, line):
        print("{",
      "\"txid\": \"c14aba0d339c7fc8d8f89a62dc7950826f2213649e71b3d79cfe105c78f7474b\",",
      "\"vout\": 1,",
      "\"scriptSig\": {",
        "\"asm\": \"0014e833cb5354dd30bdb4d0ecca6f9d986a38df629c\",",
        "\"hex\": \"160014e833cb5354dd30bdb4d0ecca6f9d986a38df629c\"",
      "},",
      "\"sequence\": 4294967294",
    "},",
    "{",
    "  \"txid\": \"34c34f48580337c6fa76a5545546a0980f57b1de516a20fcaba6b404ce4e7c96\",",
      "\"vout\": 0,",
      "\"scriptSig\": {",
        "\"asm\": \"00147f6e0f0300dbd7f57110f891e9859546afafcf88\",",
        "\"hex\": \"1600147f6e0f0300dbd7f57110f891e9859546afafcf88\"",
      "},",
      "\"sequence\": 4294967294",
    "}", sep="\n")

    def do_broadcast(self, line):
        global node_ip

        print(CRED, end="")
        try:
            url = node_ip + '/transaction/new'
            post_data = {'serialized_tx': str(TRANSACTIONS[-1])}
            resp = requests.post(url=url, json=post_data)
            code = resp.status_code
        except:
            print("[from: cli]: cannot send request", CEND)
            return False
        if code < 300:
            print(CGREEN, end="")
        for i in status_codes:
            if status_codes[i] == code:
                print("[from: node]:", i)
        print(CEND, end="")

    def do_send(self, line):
        # try:
            PRIVATE_KEYS.append("884a1c97e9feb617ece801bb13ad7251854f9f0821f2f61237accbe085be58af")         ############################ delme
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
            print(tx.get_signed_raw_format(sender_compressed_pub_key).hex())

            # tx.calculate_hash()
            # signature, verify_key = wallet_utils.signMessage(sender_private, tx.get_hash())
            # tx.set_sign(signature, verify_key)
            # if not tx_v.validate_recipient_address(tx.get_unformat_recipient_address()):
            #     raise WrongRecipientAddress
            # if not tx_v.verify_sender_address(tx.get_unformat_sender_address(), sender_private):
            #     raise WrongSenderAddress
            # if not tx_v.validate_signature(tx, (wallet_utils.getPublickKey(sender_private)).decode('utf-8')[2:]):
            #     raise WrongTransactionSignature

            # ser_tx = Serializer(tx).get_serialized_tx()
            # TRANSACTIONS.append(ser_tx)
            # print("Your raw transaction:\n", ser_tx, sep="")
        # except WrongRawTransaction:
        #     print("Raw transaction has wrong format")
        # except WrongTransactionSignature:
        #     print("Wrong transaction signature")
        #     self.help_send()
        #     return False
        # except WrongRecipientAddress:
        #     print("Wrong recipient address")
        #     self.help_send()
        #     return False
        # except WrongSenderAddress:
        #     print("Wrong sender address")
        #     self.help_send()
        #     return False
        # except AmountError:
        #     print("The amount should be from 0.1 to 6553.5")
        #     self.help_send()
        #     return False
        # except ValueError:
        #     print("Wrong amount")
        #     self.help_send()
        #     return False
        # except WrongPublicKey:                       # 84.999800
        #     print("Wrong public key")
        #     self.help_send()
        #     return False
        # except WrongLineArgs:
        #     print("should be 2 arguments")
        #     self.help_send()
        #     return False
        # except IndexError:
        #     print("Generate or import private key first")
        #     return False

    def do_endpoint(self, line):
        if len(line) < 1:
            self.help_endpoin()
            return False
        try:
            global node_ip

            line = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}\b", line)
            if len(line) < 1:
                raise WrongIp

            node_ip = 'http://' + line[0]
            url = node_ip + '/chain/length'
            requests.post(url=url, json='')
            print(CGREEN, "[from: cli]: connected", CEND, sep="")
        except WrongIp:
            print(CRED, "[from: cli]: wrong node ip", CEND, sep="")
            self.help_endpoin()
        except requests.exceptions.ConnectionError:
            print(CRED, "[from: cli]: cannot connect", CEND, sep="")

def print_keys_info(private_key):
    print("Private key: \"", private_key, "\"", sep="")
    print("Look for your public key at storage/address.txt line %d" % int(wallet_utils.getFileLines()))


if __name__ == '__main__':
    WalletCli().cmdloop()


# import storage/wifKey



"""
01000000
01
1ba58ce93e5a6e31f281f50e21881d6fce206003dc008c73ff6e273b56073403
01
0000006
b473044022071b9309a68e416d5179b2f9dfb8ee1464400eb00243a16c905797bc6ac1a6cc402204a6f81985e9fbb5f2de7733c5c82237902c9755a3c416ea55d19736045dd2066012102c3c6a89e01b4b62621233c8e0c2c26078a2449abaa837e18f96a1f65d7b8cc8c76a9149f5e9ced489eb7ed8157b533e4199aad1a9b50b288acffffffff02204e00000000000000204e0000000000000000000000
"""













