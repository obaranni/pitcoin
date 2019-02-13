import sys, os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'classes'))
from block import Block

def get_block_symb(blocks_json, start_point=None):
    if start_point is None:
        start_point = len(blocks_json) - 2
    last = -1
    first = -1
    i = start_point
    while i < len(blocks_json):
        if blocks_json[i] == '}':
            last = i
            break
        i += 1

    i = start_point
    while i >= 0:
        if blocks_json[i] == '{':
            first = i
            break
        i -= 1
    return last + 1, first


def convert_last_block_from(blocks_json):
    end, start = get_block_symb(blocks_json)
    last_block_json = json.loads(blocks_json[start:end])
    block = Block(last_block_json['timestamp'], last_block_json['prev_hash'], last_block_json['transactions'], int(last_block_json['id']), int(last_block_json['reward']), int(last_block_json['difficulty']), last_block_json['nonce'], last_block_json['hash'])
    return block


def find_block_by_id(blocks_json, id):
    sub_str = "\"id\": \"%s\"" % id
    position = blocks_json.find(sub_str, 0, len(blocks_json))
    return position


def get_str_block_by_id(blocks_json, id):
    position = find_block_by_id(blocks_json, id)
    if position == -1:
        return False
    end, start = get_block_symb(blocks_json, position)
    block_json = json.loads(blocks_json[start:end])
    return block_json


def convert_block_from(block_json):
    block = Block(block_json['timestamp'], block_json['prev_hash'], block_json['transactions'], int(block_json['id']), int(block_json['reward']), int(block_json['difficulty']), block_json['nonce'], block_json['hash'], block_json['merkle_root'])
    return block


def convert_by_id_block_from(blocks_json, id):
    block_json = get_str_block_by_id(blocks_json, id)
    if not block_json:
        return False
    block = convert_block_from(block_json)
    return block

