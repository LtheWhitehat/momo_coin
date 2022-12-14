#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:23:50 2022

@author: lilly
"""



import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse



class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash='0')
        self.nodes = set()
        
    def create_block(self, proof, previous_hash):
        block={'index': len(self.chain)+1,
               'timestamp': str(datetime.datetime.now()),
               'proof': proof,
               'previous_hash': previous_hash,
               'transactions': self.transactions
               }
        self.transactions = []
        self.chain.append(block)
        return block

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender, 
            'receiver': receiver,
            'amout':amount
        })
        block_to_transact = self.get_previous_block()['index'] + 1
        return block_to_transact

    def add_node(self, address):
        origin_netloc = urlparse(address).netloc
        self.nodes.add(origin_netloc)

    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if hash_operation[:4]=='0000':
                check_proof = True
            else:
                new_proof += 1
        
        return new_proof


    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        curr_chain_len = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code != 200:
                continue
            length = response.json()['length']
            chain = response.json()['chain']
            if length > curr_chain_len and self.is_chain_valid(chain):
                curr_chain_len = length
                longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True
        return False


    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4]!= '0000':
                return False
            previous_block = block
            block_index+=1

        return True
            

            
