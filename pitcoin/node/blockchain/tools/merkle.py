import hashlib
from binascii import unhexlify

def calculate_root_hash(data):
    hash = hashlib.sha256(bytes(data, 'utf-8')).hexdigest()
    return hash

def calculate_merkle_root(transactions):
    if len(transactions) < 1:
        return False
    if len(transactions) % 2 != 0:
        transactions.append(transactions[-1])
    roots = transactions
    merkle_root = None
    while merkle_root is None:
        new_roots = []
        if len(roots) == 1:
            merkle_root = roots[0]
            break
        for i in range(0, len(roots) - 1):
            new_roots.append(calculate_root_hash(roots[i] + roots[i + 1]))
        roots = new_roots
    return merkle_root