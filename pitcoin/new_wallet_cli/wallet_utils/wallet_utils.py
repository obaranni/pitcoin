import base58
import hashlib
import binascii
import secrets
import codecs
import ecdsa

from binascii import hexlify, unhexlify
DECIMALS = 1         # create header ???
MAX_AMOUNT = 6553.5  # 6553.5 from max short 65535 / 10

STORAGE_FILE = "storage/address.txt"

def privateKeyToWIF(privKey): #TODO: check is valid, testnet or mainnet
    pref_key = "80" + privKey
    hashed_key = hashlib.sha256(binascii.unhexlify(pref_key)).hexdigest()
    hashed_twice_key = hashlib.sha256(binascii.unhexlify(hashed_key)).hexdigest()
    checksum = hashed_twice_key[:8]
    checksum_key = pref_key + checksum
    import_format = base58.b58encode(binascii.unhexlify(checksum_key))
    return import_format


def wifKeyToPrivateKey(wifKey):
    decode_base = None
    try:
        decode_base = base58.b58decode(wifKey.encode('utf-8'))
        decode_base = codecs.encode(decode_base, 'hex')[2:-8]
    except:
        print("Bed wif key format")
        return decode_base
    return decode_base.decode('utf-8')


def readPrivateKey(filepath):   #TODO: check is file exist etc
    file = open(filepath, 'r')
    return file.readline()


def createPrivateKey(): #TODO: ? own generator,  check curve order  crossing
    new_priv_key = hex(secrets.randbits(256))[2:]
    while len(new_priv_key) < 64:
        new_priv_key = "0" + new_priv_key
    if len(new_priv_key) != 64 or new_priv_key.upper() >= "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141":
        return createPrivateKey()
    return new_priv_key


def getPublickKey(privKey):
    private_key_bytes = codecs.decode(privKey, 'hex')
    pub_key_obj = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1).get_verifying_key()
    pub_key_bytes = pub_key_obj.to_string()
    pub_key_hex = b"04" + hexlify(pub_key_bytes)
    return pub_key_hex


def compressPublicKey(pubKey):
    comp_key = pubKey[2:66]
    if int(pubKey[-2:], 16) % 2 == 0:
        comp_key = b"02" + comp_key
    else:
        comp_key = b"03" + comp_key
    return comp_key


def getAddresOfPublicKey(pubKey, testnet=0):
    sha = hashlib.new('sha256', codecs.decode(pubKey, 'hex')).digest()
    ripemd = hashlib.new('ripemd160', sha).digest()
    if testnet:
        encr_pub = codecs.decode("6f", 'hex') + ripemd
    else:
        encr_pub = codecs.decode("00", 'hex') + ripemd
    checksum = hashlib.new('sha256', hashlib.new('sha256', encr_pub).digest()).digest()
    return base58.b58encode(codecs.decode(codecs.encode(encr_pub + checksum[:4], 'hex'), 'hex')).decode('utf-8')


def fullSettlementPublicAddress(privKey):
    pub_key = getPublickKey(privKey)
    compressed_pub_key = compressPublicKey(pub_key)
    pub_address = getAddresOfPublicKey(compressed_pub_key)
    return pub_address


def signMessage(priv_key, message_to_sign): #TODO: cmp sign with online signer
    message_to_sign = bytes(message_to_sign, 'utf-8')
    sign_key = ecdsa.SigningKey.from_string(codecs.decode(priv_key, 'hex'), ecdsa.SECP256k1)
    verify_key = sign_key.get_verifying_key()
    signature = sign_key.sign(message_to_sign)
    assert verify_key.verify(signature, message_to_sign)
    return signature, verify_key


def getFileLines():
    file = open(STORAGE_FILE, "a+")
    lines = sum(1 for line in open(STORAGE_FILE))
    file.close()
    return lines


def saveKeyToFile(key):
    file = open(STORAGE_FILE, "a+")
    file.write("Public address: %s\n" % key)
    file.close()


def readKeyFromFile(filePath):
    key = None
    try:
        file = open(filePath, "r")
        key = file.readline()
    except FileNotFoundError as err:
        print("Reading key from file error:", err)
    except IsADirectoryError as err:
        print("Reading key from file error:", err)
    return key


def newKeyPair(testnet=0):
    privKey = createPrivateKey()
    pubKey = getPublickKey(privKey)
    compPubKey = compressPublicKey(pubKey)
    address = getAddresOfPublicKey(compPubKey, testnet)
    return privKey, pubKey, address


def main(): # TODO change key storing format to bytes
    priv_key = createPrivateKey()
    wif_priv_key = privateKeyToWIF(priv_key)
    pass
    # signature, verKey = signMessage(privKey, b"abc")
    # print(codecs.encode(signature, 'hex'), "\n", codecs.encode(verKey, 'hex'))
    #
    # print("sign", b"abc")


if __name__ == "__main__":
    STORAGE_FILE = "../storage/address.txt"
    main()
