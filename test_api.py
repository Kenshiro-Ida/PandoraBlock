import requests
import json
from datetime import datetime, timedelta
from pprint import pprint
from time import sleep
from eth_utils import to_checksum_address
from web3 import Web3
import random
import uuid

BASE_URL = 'http://localhost:5000'

# Initialize Web3
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

def get_accounts():
    """Get available accounts from Ganache"""
    return w3.eth.accounts

def check_health():
    """Check if the blockchain system is running and connected"""
    try:
        response = requests.get(f'{BASE_URL}/health')
        print("\n=== Health Check ===")
        pprint(response.json())
        return response.json()['blockchain_connected']
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
        return False

def register_product(product_data):
    """Register a new pharmaceutical product"""
    try:
        response = requests.post(
            f'{BASE_URL}/product/register',
            json=product_data
        )
        print(f"\n=== Registering Product: {product_data['product_id']} ===")
        result = response.json()
        pprint(result)
        
        if result['status'] == 'error':
            print(f"Error registering product: {result['message']}")
            return None
            
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

def transfer_product(transfer_data):
    """Transfer product ownership"""
    try:
        # Ensure the address is in checksum format
        transfer_data['new_owner'] = to_checksum_address(transfer_data['new_owner'])
        
        response = requests.post(
            f'{BASE_URL}/product/transfer',
            json=transfer_data
        )
        print(f"\n=== Transferring Product: {transfer_data['product_id']} ===")
        result = response.json()
        pprint(result)
        
        if result['status'] == 'error':
            print(f"Error transferring product: {result['message']}")
            return None
            
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

def verify_product(product_id, serial_number):
    """Verify product authenticity and get its history"""
    try:
        response = requests.get(
            f'{BASE_URL}/product/verify/{product_id}/{serial_number}'
        )
        print(f"\n=== Verifying Product: {product_id} ===")
        result = response.json()
        pprint(result)
        
        if result['status'] == 'error':
            print(f"Error verifying product: {result['message']}")
            return None
            
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

def generate_random_product_data():
    """Generate random product data for testing"""
    product_id = f"PROD-{uuid.uuid4().hex[:8]}"  # Random product ID
    serial_number = f"SN-{uuid.uuid4().hex[:8]}"  # Random serial number
    batch_number = f"BATCH-{random.randint(1000, 9999)}"  # Random batch number
    manufacturer = random.choice(["PharmaCorp", "SecurePharm", "BioTech"])
    manufacture_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
    expiry_date = (datetime.now() + timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d')
    gtin = f"05901234{random.randint(100000, 999999)}"  # Random GTIN

    return {
        "product_id": product_id,
        "manufacturer": manufacturer,
        "batch_number": batch_number,
        "manufacture_date": manufacture_date,
        "expiry_date": expiry_date,
        "gtin": gtin,
        "serial_number": serial_number
    }

def main():
    # First, check if the system is healthy
    if not check_health():
        print("Blockchain system is not connected!")
        return

    # Get available accounts from Ganache
    accounts = get_accounts()
    if not accounts:
        print("No accounts available from Ganache!")
        return

    # Use different accounts for different roles
    manufacturer = accounts[0]
    distributor = accounts[1]
    pharmacy = accounts[2]

    print(f"\nUsing accounts:")
    print(f"Manufacturer: {manufacturer}")
    print(f"Distributor: {distributor}")
    print(f"Pharmacy: {pharmacy}")

    # Example 1: Register a basic medication
    basic_med = generate_random_product_data()
    reg_result = register_product(basic_med)
    if not reg_result:
        return
    sleep(2)  # Wait for blockchain transaction

    # Example 2: Register a controlled substance
    controlled_med = generate_random_product_data()
    reg_result = register_product(controlled_med)
    if not reg_result:
        return
    sleep(2)

    # Example 3: Register a vaccine
    vaccine = generate_random_product_data()
    reg_result = register_product(vaccine)
    if not reg_result:
        return
    sleep(2)

    # Example 4: Transfer medication to distributor
    transfer_1 = {
        "product_id": basic_med['product_id'],
        "serial_number": basic_med['serial_number'],
        "new_owner": distributor,
        "transfer_type": "Manufacturer-to-Distributor"
    }
    transfer_result = transfer_product(transfer_1)
    if not transfer_result:
        return
    sleep(2)

    # Example 5: Transfer from distributor to pharmacy
    transfer_2 = {
        "product_id": basic_med['product_id'],
        "serial_number": basic_med['serial_number'],
        "new_owner": pharmacy,
        "transfer_type": "Distributor-to-Pharmacy"
    }
    transfer_result = transfer_product(transfer_2)
    if not transfer_result:
        return
    sleep(2)

    # Example 6: Verify products
    print("\nVerifying products...")
    verify_product(basic_med['product_id'], basic_med['serial_number'])
    verify_product(controlled_med['product_id'], controlled_med['serial_number'])
    verify_product(vaccine['product_id'], vaccine['serial_number'])

def test_single_transfer():
    """Test a single transfer with proper error handling"""
    accounts = get_accounts()
    if not accounts:
        print("No accounts available from Ganache!")
        return

    transfer_data = {
        "product_id": f"PROD-{uuid.uuid4().hex[:8]}",
        "serial_number": f"SN-{uuid.uuid4().hex[:8]}",
        "new_owner": accounts[1],  # Use the second account as the receiver
        "transfer_type": "Manufacturer-to-Distributor"
    }
    
    result = transfer_product(transfer_data)
    if result and result['status'] == 'success':
        print("Transfer successful!")
        verify_product(transfer_data['product_id'], transfer_data['serial_number'])

if __name__ == "__main__":
    print("Choose test to run:")
    print("1. Run full test suite")
    print("2. Test single transfer")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        main()
    elif choice == "2":
        test_single_transfer()
    else:
        print("Invalid choice!")
