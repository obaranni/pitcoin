import sys, os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'classes'))
from block import Block

def convert_blocks_from(blocks_json):
    blocks_json = '{\n' + blocks_json + '}'
    print(json.loads(blocks_json))
    # blocks = [Block(i['timestamp'], i['prev_hash'], i['transactions'], i['nonce'], i['hash']) for i in block_dict['blocks']]
    # return blocks

def get_last_block_symb(blocks_json, symb):
    last = -1
    for i in range(0, len(blocks_json)):
        if blocks_json[i] == symb:
            last = i
    return last


def convert_last_block_from(blocks_json):
    end = get_last_block_symb(blocks_json, '}')
    start = get_last_block_symb(blocks_json, '{')
    last_block_json = json.loads(blocks_json[start:end + 1])
    block = Block(last_block_json['timestamp'], last_block_json['prev_hash'], last_block_json['transactions'], int(last_block_json['id']), last_block_json['nonce'], last_block_json['hash'])
    return block

