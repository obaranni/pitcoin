import sys, os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'classes'))
from block import Block

def convert_blocks_from(file_json):
    block_dict = json.load(file_json)

    blocks = [Block(i['timestamp'], i['prev_hash'], i['timestamp'], i['nonce']) for i in block_dict['blocks']]


