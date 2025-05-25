# simulate_supply_chain.py
import requests
import json
from datetime import datetime, timedelta
from pprint import pprint
from time import sleep
import random

BASE_URL = 'http://localhost:5000'

class SupplyChainSimulator:
    def __init__(self):
        # Simulated blockchain addresses for different parties
        self.participants = {
            'manufacturer': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'distributor': '0x742d35Cc6634C0532925a3b844Bc454e4438f44f',
            'wholesaler': '0x742d35Cc6634C0532925a3b844Bc454e4438f450',
            'pharmacy_1': '0x742d35Cc6634C0532925a3b844Bc454e4438f451',
            'pharmacy_2': '0x742d35Cc6634C0532925a3b844Bc454e4438f452',
            'hospital': '0x742d35Cc6634C0532925a3b844Bc454e4438f453'
        }
        
        # Product templates
        self.product_templates = {
            'antibiotics': {
                'base_id': 'ANT',
                'manufacturer': 'PharmaCorp',
                'shelf_life_days': 730  # 2 years
            },
            'vaccines': {
                'base_id': 'VAX',
                'manufacturer': 'BioTech',
                'shelf_life_days': 180  # 6 months
            },
            'controlled': {
                'base_id': 'CTR',
                'manufacturer': 'SecurePharm',
                'shelf_life_days': 365  # 1 year
            }
        }

    def generate_batch(self, product_type, batch_size=5):
        """Generate a batch of products of the specified type"""
        template = self.product_templates[product_type]
        batch_number = f"BATCH{random.randint(1000, 9999)}"
        batch_products = []

        for i in range(batch_size):
            product = {
                "product_id": f"{template['base_id']}{random.randint(100, 999)}",
                "manufacturer": template['manufacturer'],
                "batch_number": batch_number,
                "manufacture_date": datetime.now().strftime('%Y-%m-%d'),
                "expiry_date": (datetime.now() + timedelta(days=template['shelf_life_days'])).strftime('%Y-%m-%d'),
                "gtin": f"0590123{random.randint(1000000, 9999999)}",
                "serial_number": f"SER{random.randint(10000, 99999)}"
            }
            batch_products.append(product)

        return batch_products

    def register_batch(self, products):
        """Register a batch of products"""
        results = []
        for product in products:
            response = requests.post(f'{BASE_URL}/product/register', json=product)
            results.append(response.json())
            sleep(1)  # Wait for blockchain transaction
        return results

    def transfer_batch(self, products, from_party, to_party, transfer_type):
        """Transfer a batch of products between parties"""
        results = []
        for product in products:
            transfer_data = {
                "product_id": product["product_id"],
                "serial_number": product["serial_number"],
                "new_owner": self.participants[to_party],
                "transfer_type": transfer_type
            }
            response = requests.post(f'{BASE_URL}/product/transfer', json=transfer_data)
            results.append(response.json())
            sleep(1)
        return results

    def verify_batch(self, products):
        """Verify a batch of products"""
        results = []
        for product in products:
            response = requests.get(
                f'{BASE_URL}/product/verify/{product["product_id"]}/{product["serial_number"]}'
            )
            results.append(response.json())
        return results

def main():
    # Initialize simulator
    simulator = SupplyChainSimulator()

    # Check system health
    response = requests.get(f'{BASE_URL}/health')
    if not response.json()['blockchain_connected']:
        print("Blockchain system is not connected!")
        return

    print("\n=== Starting Supply Chain Simulation ===")

    # Generate and register products
    print("\n1. Generating and registering products...")
    antibiotics = simulator.generate_batch('antibiotics', 3)
    vaccines = simulator.generate_batch('vaccines', 2)
    controlled = simulator.generate_batch('controlled', 2)

    print("\nRegistering antibiotics batch...")
    simulator.register_batch(antibiotics)
    print("\nRegistering vaccines batch...")
    simulator.register_batch(vaccines)
    print("\nRegistering controlled substances batch...")
    simulator.register_batch(controlled)

    # Simulate supply chain movements
    print("\n2. Simulating supply chain transfers...")

    # Transfer antibiotics: Manufacturer -> Distributor -> Wholesaler -> Pharmacy
    print("\nTransferring antibiotics through supply chain...")
    simulator.transfer_batch(antibiotics, 'manufacturer', 'distributor', 'Manufacturer-to-Distributor')
    sleep(2)
    simulator.transfer_batch(antibiotics, 'distributor', 'wholesaler', 'Distributor-to-Wholesaler')
    sleep(2)
    simulator.transfer_batch(antibiotics, 'wholesaler', 'pharmacy_1', 'Wholesaler-to-Pharmacy')

    # Transfer vaccines: Manufacturer -> Distributor -> Hospital
    print("\nTransferring vaccines through supply chain...")
    simulator.transfer_batch(vaccines, 'manufacturer', 'distributor', 'Manufacturer-to-Distributor')
    sleep(2)
    simulator.transfer_batch(vaccines, 'distributor', 'hospital', 'Distributor-to-Hospital')

    # Transfer controlled substances: Manufacturer -> Distributor -> Pharmacy
    print("\nTransferring controlled substances through supply chain...")
    simulator.transfer_batch(controlled, 'manufacturer', 'distributor', 'Manufacturer-to-Distributor')
    sleep(2)
    simulator.transfer_batch(controlled, 'distributor', 'pharmacy_2', 'Distributor-to-Pharmacy')

    # Verify products at different stages
    print("\n3. Verifying products...")
    print("\nVerifying antibiotics:")
    pprint(simulator.verify_batch(antibiotics))
    print("\nVerifying vaccines:")
    pprint(simulator.verify_batch(vaccines))
    print("\nVerifying controlled substances:")
    pprint(simulator.verify_batch(controlled))

if __name__ == "__main__":
    main()