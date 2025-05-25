# app.py
from flask import Flask, request, jsonify
from web3 import Web3
import json
from datetime import datetime
import os
from pathlib import Path
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Connect to Ganache
# w3 = Web3(Web3.HTTPProvider(' https://brief-presently-ladybug.ngrok-free.app'))
w3 = Web3(Web3.HTTPProvider(' http://127.0.0.1:7545'))
# Updated path to contract JSON
contract_path = Path('build/contracts/PharmaSupplyChain.json')
if not contract_path.exists():
    raise FileNotFoundError(
        "Contract JSON not found. Please ensure you have run 'truffle migrate' successfully"
    )

# Load smart contract ABI and address
with open(contract_path) as f:
    contract_json = json.load(f)
CONTRACT_ABI = contract_json['abi']

# Get the most recently deployed contract address
CONTRACT_ADDRESS = contract_json['networks'][list(contract_json['networks'].keys())[-1]]['address']

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def format_product_info(product_tuple):
    """Format product information from contract tuple response"""
    try:
        return {
            'product_id': product_tuple[0],
            'manufacturer': product_tuple[1],
            'batch_number': product_tuple[2],
            'manufacture_date': datetime.fromtimestamp(product_tuple[3]).isoformat(),
            'expiry_date': datetime.fromtimestamp(product_tuple[4]).isoformat(),
            'current_owner': product_tuple[5],
            'gtin': product_tuple[6],
            'serial_number': product_tuple[7]
        }
    except Exception as e:
        app.logger.error(f"Error formatting product info: {e}")
        return None

def format_transfer(transfer_tuple):
    """Format transfer information from contract tuple response"""
    try:
        return {
            'from': transfer_tuple[0],
            'to': transfer_tuple[1],
            'timestamp': datetime.fromtimestamp(transfer_tuple[2]).isoformat(),
            'transfer_type': transfer_tuple[3]
        }
    except Exception as e:
        app.logger.error(f"Error formatting transfer info: {e}")
        return None

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'blockchain_connected': w3.is_connected(),
        'current_block': w3.eth.block_number,
        'contract_address': CONTRACT_ADDRESS
    })

@app.route('/product/register', methods=['POST'])
def register_product():
    try:
        data = request.get_json()
        
        # Get transaction sender address
        sender_address = w3.eth.accounts[0]
        
        # Build transaction
        nonce = w3.eth.get_transaction_count(sender_address)
        
        tx = contract.functions.registerProduct(
            data['product_id'],
            data['manufacturer'],
            data['batch_number'],
            int(datetime.strptime(data['manufacture_date'], '%Y-%m-%d').timestamp()),
            int(datetime.strptime(data['expiry_date'], '%Y-%m-%d').timestamp()),
            data['gtin'],
            data['serial_number']
        ).build_transaction({
            'from': sender_address,
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        })
        
        # Sign and send transaction
        private_key = os.getenv('PRIVATE_KEY')
        if not private_key:
            # Use the first account's private key from Ganache for testing
            private_key = w3.eth.account.from_key(os.getenv('PRIVATE_KEY', '0xef704a92be65bc0102ebb7b19418dc0a9b14ca7bd2ab01ff5aa0edd72d4fbfef'))
            
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return jsonify({
            'status': 'success',
            'transaction_hash': tx_hash.hex(),
            'block_number': tx_receipt['blockNumber']
        })
        
    except Exception as e:
        app.logger.error(f"Error in register_product: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/product/transfer', methods=['POST'])
def transfer_product():
    try:
        # Log incoming request data
        data = request.get_json()
        if not data:
            app.logger.error("No JSON data received in request")
            return jsonify({
                'status': 'error',
                'message': 'Request must contain JSON data'
            }), 400

        # Validate required fields
        required_fields = ['product_id', 'serial_number', 'new_owner', 
                         'transfer_type', 'sender_address', 'private_key']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            app.logger.error(f"Missing required fields: {missing_fields}")
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {missing_fields}'
            }), 400

        # Validate address formats
        if not w3.is_address(data['sender_address']):
            app.logger.error(f"Invalid sender address format: {data['sender_address']}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid sender address format'
            }), 400

        if not w3.is_address(data['new_owner']):
            app.logger.error(f"Invalid new owner address format: {data['new_owner']}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid new owner address format'
            }), 400

        # Validate private key format
        try:
            if not data['private_key'].startswith('0x'):
                data['private_key'] = '0x' + data['private_key']
            w3.eth.account.from_key(data['private_key'])
        except Exception as e:
            app.logger.error(f"Invalid private key format: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid private key format'
            }), 400

        # Check if product exists
        try:
            product_info = contract.functions.getProductInfo(
                data['product_id'], 
                data['serial_number']
            ).call()
        except Exception as e:
            app.logger.error(f"Error checking product existence: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Product does not exist or error checking product'
            }), 404

        # Verify sender is current owner
        if product_info[5].lower() != data['sender_address'].lower():
            app.logger.error(f"Sender {data['sender_address']} is not the current owner {product_info[5]}")
            return jsonify({
                'status': 'error',
                'message': 'Sender is not the current owner of the product'
            }), 403

        # Build the transaction
        try:
            nonce = w3.eth.get_transaction_count(data['sender_address'])
            
            tx = contract.functions.transferProduct(
                data['product_id'],
                data['serial_number'],
                data['new_owner'],
                data['transfer_type']
            ).build_transaction({
                'from': data['sender_address'],
                'gas': 2000000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
            })
            
            # Sign and send the transaction
            signed_tx = w3.eth.account.sign_transaction(tx, private_key=data['private_key'])
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for transaction receipt
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            app.logger.info(f"Transfer successful. Transaction hash: {tx_hash.hex()}")
            return jsonify({
                'status': 'success',
                'transaction_hash': tx_hash.hex(),
                'block_number': tx_receipt['blockNumber']
            })
            
        except Exception as e:
            app.logger.error(f"Transaction error: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Transaction failed: {str(e)}'
            }), 400
            
    except Exception as e:
        app.logger.error(f"Unexpected error in transfer_product: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/product/verify/<product_id>/<serial_number>')
def verify_product(product_id, serial_number):
    try:
        # Get product info from contract
        product_info = contract.functions.getProductInfo(product_id, serial_number).call()
        print(product_info)
        formatted_product = format_product_info(product_info)
        
        if not formatted_product:
            return jsonify({
                'status': 'error',
                'message': 'Error formatting product information'
            }), 400

        # Get transfer history from contract
        transfer_history = contract.functions.getTransferHistory(product_id, serial_number).call()
        print(transfer_history)
        formatted_transfers = [
            format_transfer(transfer) for transfer in transfer_history
        ]
        
        # Remove any None values from failed transfer formatting
        formatted_transfers = [t for t in formatted_transfers if t is not None]
        
        return jsonify({
            'status': 'success',
            'product_info': formatted_product,
            'transfer_history': formatted_transfers
        })
        
    except Exception as e:
        app.logger.error(f"Error in verify_product: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)