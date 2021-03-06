import json

# block id (height)
# hash
# previous hash
# nonce
# timestamp
# merkle_root
# transactions

def convert_blocks_to(blocks):
    json_blocks = json.JSONDecoder().decode(
        json.dumps([json.JSONDecoder().decode(
            json.dumps({'id': str(blocks[i].block_id), 'prev_hash': str(blocks[i].previous_hash),
                        'hash': str(blocks[i].hash),
                        'reward': blocks[i].reward,
                        'difficulty': blocks[i].difficulty,
                        'nonce': blocks[i].nonce, 'timestamp': blocks[i].timestamp,
                                'merkle_root': blocks[i].merkle_root,
                                'transactions': json.JSONDecoder().decode(json.dumps(
                                    [blocks[i].transactions[j] for j in range(0, len(blocks[i].transactions))], indent=4))}, indent=4))
                    for i in range(0, len(blocks))], indent=4))
    return json_blocks
