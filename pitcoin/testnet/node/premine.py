import blockchain.tools.wallet as wlt
from blockchain.tools.serializer import Serializer
from blockchain.classes.transaction import Transaction
from blockchain.tools import tx_validator as tx_v
import requests
from random import  randint, randrange

status_codes = {
    "Transaction pull i empty": 101,
    "Node added": 102,
    "Cannot start mine mode": 103,
    "Transaction pended": 201,
    "Bad json format": 401,
    "Bad transaction": 402,
}

TRANSACTIONS = []
DECIMALS = 1
MAX_AMOUNT = 6553.5
STORAGE_FILE1 = "address1"
STORAGE_FILE2 = "address2"
STORAGE_FILE3 = "address3"
node_ip = 'http://127.0.0.1:5000'
CRED = '\033[91m'
CGREEN = '\033[92m'
CEND = '\033[0m'

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

def do_broadcast():
    global node_ip

    print(CRED)
    try:
        url = node_ip + '/transaction/new'
        post_data = {'serialized_tx': str(TRANSACTIONS[-1])}
        resp = requests.post(url=url, json=post_data)
        code = resp.status_code
    except:
        print("[from: cli]: cannot send request", CEND)
        return False
    if code < 300:
        print(CGREEN)
    for i in status_codes:
        if status_codes[i] == code:
            print("[from: node]:", i)
    print(CEND, end="")


def do_send(priv_key, line):
    try:
        lines = str(line).split()
        if len(lines) != 2:
            raise WrongLineArgs
        recipient = str(lines[0])
        amount = float(lines[1])
        print(amount, amount < 0.1)
        if amount > MAX_AMOUNT or amount < 0.1 or len(str(amount).split('.')[1]) > DECIMALS:
            raise AmountError
        pitoshi = "{0:0{1}x}".format(int(amount * int(pow(10, DECIMALS))), 4)
        sender_pub = wlt.fullSettlementPublicAddress(priv_key)
        tx = Transaction(sender_pub, recipient,
                         bytes(pitoshi.encode('utf-8')).decode('utf-8'))
        tx.calculate_hash()
        signature, verify_key = wlt.signMessage(priv_key, tx.get_hash())
        tx.set_sign(signature, verify_key)
        if not tx_v.validate_recipient_address(tx.get_unformat_recipient_address()):
            raise WrongRecipientAddress
        if not tx_v.verify_sender_address(tx.get_unformat_sender_address(), priv_key):
            raise WrongSenderAddress
        if not tx_v.validate_signature(tx, (wlt.getPublickKey(priv_key)).decode('utf-8')[2:]):
            raise WrongTransactionSignature

        ser_tx = Serializer(tx).get_serialized_tx()
        TRANSACTIONS.append(ser_tx)
        # print("Your raw transaction:\n", ser_tx, sep="")
    except WrongRawTransaction:
        print("Raw transaction has wrong format")
    except WrongTransactionSignature:
        print("Wrong transaction signature")
        return False
    except WrongRecipientAddress:
        print("Wrong recipient address")
        return False
    except WrongSenderAddress:
        print("Wrong sender address")
        return False
    except AmountError:
        print("The amount should be from 0.1 to 6553.5")
        return False
    except ValueError:
        print("Wrong amount")
        return False
    except WrongPublicKey:  # 84.999800
        print("Wrong public key")
        return False
    except WrongLineArgs:
        print("Wrong send arguments")
        return False
    except IndexError:
        print("Generate or import private key first")
        return False





priv = [0, 0, 0]
addr = [0, 0, 0]

priv[0], pub1, addr[0] = wlt.newKeyPair()
priv[1], pub2, addr[1] = wlt.newKeyPair()
priv[2], pub3, addr[2] = wlt.newKeyPair()

file1 = open(STORAGE_FILE1, 'w+')
file2 = open(STORAGE_FILE2, 'w+')
file3 = open(STORAGE_FILE3, 'w+')

file1.write("Address: %s" % addr[0])
file2.write("Address: %s" % addr[1])
file3.write("Address: %s" % addr[2])

file1.close()
file2.close()
file3.close()

print("Your private key: %s, look for your public key in file address1" % priv[0])
print("Your private key: %s, look for your public key in file address2" % priv[1])
print("Your private key: %s, look for your public key in file address3" % priv[2])


print("tx", 0)
do_send(priv[0], str(addr[0]) + "  40")
do_broadcast()
for i in range(0, 35):
    print("tx", i + 1)
    sender = randrange(0, 2)
    recipient = randrange(0, 2)
    print("sender", addr[sender], "recipient", addr[recipient])
    do_send(priv[sender], str(addr[recipient]) + " 1")
    do_broadcast()
