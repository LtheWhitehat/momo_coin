#from .blockchain import Blockchain
import momo_coin as Blockchain
from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)

node_address = str(uuid4()).replace('-', '')
print(node_address)

blockchain = Blockchain.Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    blockchain.add_transaction(sender=node_address, receiver='Lillian', 3)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {
        'message': 'Congratulations, you just mined a block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'hash_anterior': block['previous_hash'],
        'transaction': block['transactions']
    }
    
    return jsonify(response), 200
    
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200
    
    

@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Preencha a transação por completo.', 400

    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = ('Message': f'Transaction will be added to the block {index}')
    return jsonify(response, 201)


@app.route('connect_node', methods=["POST"])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "Empty", 400

    for node in nodes:
        blockchain.add_node(node)
    response = {
        'Message': 'All nodes are connected.', 
        'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201


@app.route('/replace_chain', method=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {
            'message': 'There were a conflict between nodes! Your chain has been replaced with the consensus protocol',
            'chain': blockchain.chain
        }
    else:
        response = {
            'message': 'There were no substitution on the chain',
            'chain': blockchain.chain
        }

    return jsonify(response), 201



app.run(host='0.0.0.0', port=5000)