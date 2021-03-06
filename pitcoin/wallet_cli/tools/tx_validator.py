import ecdsa
import codecs
import wallet_utils


def validate_address(address):
    if len(address) > 35 or len(address) < 26 or \
            not (address[0] == "m" or address[0] == "n"):
        return False
    return True


def verify_sender_address(address, private_key):
    if address != wallet_utils.fullSettlementPublicAddress(private_key):
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
