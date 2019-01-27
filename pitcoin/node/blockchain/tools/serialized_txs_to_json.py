import json
def txs_to_json(ser_txs):
	json_txs = None
	json_txs = json.JSONDecoder().decode(
		json.dumps([json.JSONDecoder().decode(
		json.dumps({'txid':i, 'ser_tx':ser_txs[i]})) for i in range(0, len(ser_txs))]))
	return json.dumps(json_txs)
