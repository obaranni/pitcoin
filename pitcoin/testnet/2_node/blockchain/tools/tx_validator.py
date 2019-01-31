import ecdsa
import codecs
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'wallet'))
import wallet


def validate_recipient_address(address):
    if len(address) > 35 or len(address) < 26 or \
            not (address[0] == "1" or address[0] == "3" or address[:3] == "bc1"):
        return False
    return True


def verify_sender_address(address, private_key):
    if address != wallet.fullSettlementPublicAddress(private_key):
        return False
    return True


def validate_signature(tx, pub_key):
    try:
        vk = ecdsa.VerifyingKey.from_string(codecs.decode(pub_key, 'hex'), curve=ecdsa.SECP256k1)
        tx.calculate_hash()
    except:
        return False
    if not vk.verify(tx.get_sign(), bytes(tx.get_hash(), 'utf-8')):  # True
        return False
    return True
