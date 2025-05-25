# Pandora Blockchain - Pharmaceutical Supply Chain Management

A comprehensive blockchain-based solution for pharmaceutical supply chain tracking and verification, ensuring product authenticity and transparency throughout the distribution process.

## 🌟 Overview

Pandora Blockchain is a decentralized application (DApp) that leverages Ethereum smart contracts to create an immutable record of pharmaceutical products as they move through the supply chain. The system enables manufacturers, distributors, wholesalers, pharmacies, and hospitals to register, transfer, and verify pharmaceutical products securely.

## 🏗️ System Architecture

The system consists of four main components:

1. **Smart Contracts** (Solidity) - Core blockchain logic
2. **Backend API** (Python Flask) - REST API interface
3. **Mobile App** (Flutter/Dart) - Product verification interface
4. **Simulation Tools** (Python) - Testing and demonstration

## 📋 Features

### Core Functionality
- **Product Registration**: Register pharmaceutical products with detailed metadata
- **Ownership Transfer**: Secure transfer of products between supply chain participants
- **Product Verification**: Verify product authenticity and view complete history
- **QR Code Scanning**: Mobile app integration for quick product verification
- **Transfer History**: Complete audit trail of all product movements

### Security Features
- Blockchain-based immutable records
- Address-based ownership verification
- Private key authentication for transfers
- Smart contract validation

## 🔧 Smart Contracts

### PharmaSupplyChain.sol
Main contract handling:
- Product registration and metadata storage
- Ownership transfers between participants
- Transfer history tracking
- Product verification queries

### Migrations.sol
Standard Truffle migrations contract for deployment management.

## 🚀 Getting Started

### Prerequisites
- Node.js (v14+)
- Python (3.7+)
- Truffle Suite
- Ganache (for local blockchain)
- Flutter SDK (for mobile app)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pandora-blockchain
   ```

2. **Install dependencies**
   ```bash
   # Install Node.js dependencies
   npm install

   # Install Python dependencies
   pip install flask web3 flask-cors requests
   ```

3. **Set up local blockchain**
   ```bash
   # Start Ganache on port 7545
   ganache-cli -p 7545 -d
   ```

4. **Deploy smart contracts**
   ```bash
   truffle migrate --reset
   ```

5. **Start the Flask API**
   ```bash
   python app.py
   ```

### Configuration

Update the following configurations based on your setup:

**Flask API (app.py)**:
```python
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
```

**Mobile App (main.dart)**:
```dart
final String rpcUrl = "http://your-api-endpoint";
final String contractAddress = "your-contract-address";
```

## 📱 API Endpoints

### Health Check
```
GET /health
```
Returns system status and blockchain connection info.

### Product Registration
```
POST /product/register
```
Register a new pharmaceutical product.

**Request Body:**
```json
{
  "product_id": "ANT123",
  "manufacturer": "PharmaCorp",
  "batch_number": "BATCH1234",
  "manufacture_date": "2024-01-15",
  "expiry_date": "2026-01-15",
  "gtin": "0590123456789",
  "serial_number": "SER12345"
}
```

### Product Transfer
```
POST /product/transfer
```
Transfer product ownership.

**Request Body:**
```json
{
  "product_id": "ANT123",
  "serial_number": "SER12345",
  "new_owner": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
  "transfer_type": "Manufacturer-to-Distributor",
  "sender_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
  "private_key": "0xef704a92be65bc0102ebb7b19418dc0a9b14ca7bd2ab01ff5aa0edd72d4fbfef"
}
```

### Product Verification
```
GET /product/verify/{product_id}/{serial_number}
```
Verify product and retrieve complete history.

## 📱 Mobile Application

The Flutter mobile app provides:
- Manual product ID and serial number entry
- QR code scanning for quick verification
- Product information display
- Transfer history visualization

### Key Features:
- Cross-platform (iOS/Android)
- Real-time blockchain queries
- Intuitive user interface
- Offline QR code generation support

## 🧪 Testing & Simulation

Use the provided simulation script to test the complete supply chain flow:

```bash
python simulate_supply_chain.py
```

The simulation demonstrates:
- Batch product registration
- Multi-party transfers (Manufacturer → Distributor → Wholesaler → Pharmacy)
- Product verification at each stage
- Different product types (antibiotics, vaccines, controlled substances)

## 🔗 Supply Chain Participants

The system supports various participant types:
- **Manufacturers**: Register and produce pharmaceutical products
- **Distributors**: Receive products from manufacturers
- **Wholesalers**: Intermediate distribution points
- **Pharmacies**: End-point retail distribution
- **Hospitals**: Healthcare facility endpoints

## 🛡️ Security Considerations

- **Private Key Management**: Securely store and manage private keys
- **Address Validation**: All Ethereum addresses are validated
- **Ownership Verification**: Only current owners can transfer products
- **Transaction Signing**: All transfers require cryptographic signatures

## 🚨 Important Notes

- This is a demonstration/prototype system
- Use test networks for development
- Implement proper key management for production
- Consider gas optimization for large-scale deployment
- Add proper error handling and logging for production use

## 📊 Data Flow

1. **Registration**: Manufacturer registers products with metadata
2. **Transfer**: Products move through supply chain with recorded transfers
3. **Verification**: Any party can verify product authenticity and history
4. **Audit**: Complete immutable audit trail available

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Troubleshooting

### Common Issues:
- **Contract not found**: Ensure contracts are deployed after starting Ganache
- **Connection errors**: Verify API endpoints and blockchain connection
- **Transaction failures**: Check gas limits and account balances
- **Mobile app issues**: Ensure correct RPC URL and contract address

### Getting Help:
- Check the issues section for known problems
- Review the simulation script for usage examples
- Ensure all dependencies are correctly installed

## 🔮 Future Enhancements

- Integration with IoT sensors for environmental monitoring
- Advanced analytics and reporting
- Multi-chain support
- Enhanced mobile features
- Regulatory compliance modules
- Integration with existing ERP systems

---

**Note**: This system is designed for educational and demonstration purposes. For production deployment, additional security measures, testing, and compliance considerations should be implemented.
