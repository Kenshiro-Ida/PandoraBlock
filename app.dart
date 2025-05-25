import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:web3dart/web3dart.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const ProductVerificationApp());
}

class ProductVerificationApp extends StatelessWidget {
  const ProductVerificationApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Product Verification',
      theme: ThemeData(
        primarySwatch: Colors.purple,
      ),
      home: const ProductVerificationPage(),
    );
  }
}

class ProductVerificationPage extends StatefulWidget {
  const ProductVerificationPage({super.key});

  @override
  _ProductVerificationPageState createState() =>
      _ProductVerificationPageState();
}

class _ProductVerificationPageState extends State<ProductVerificationPage> {
  final TextEditingController _productIdController = TextEditingController();
  final TextEditingController _serialNumberController = TextEditingController();

  MobileScannerController cameraController = MobileScannerController();

  final String rpcUrl = "https://58e7-103-214-118-233.ngrok-free.app"; // Ganache RPC URL
  final String contractAddress = "0xb8e51d3c192ae7Fe0d4a0092cab345e5e65970C6"; // Corrected contract address
  late Web3Client web3client;
  bool isLoading = false;

  @override
  void initState() {
    super.initState();
    web3client = Web3Client(rpcUrl, http.Client()); // Initialize the Web3 client
  }

  /// Function to load ABI from JSON file
  Future<String> loadAbiFromFile(String filePath) async {
    try {
      final abiString = await rootBundle.loadString(filePath);
      final jsonMap = jsonDecode(abiString);
      return jsonEncode(jsonMap['abi']); // Extract and return the ABI as a JSON string
    } catch (e) {
      throw Exception("Error loading ABI file: $e");
    }
  }

  /// Function to load the contract from the ABI and contract address
  Future<DeployedContract> loadContract() async {
    final abi = await loadAbiFromFile('assets/PharmaSupplyChain.json'); // Make sure to place ABI file in assets
    final contractAbi = ContractAbi.fromJson(abi, 'PharmaSupplyChain');
    return DeployedContract(contractAbi, EthereumAddress.fromHex(contractAddress));
  }

  /// Function to format product information
  Future<Map<String, dynamic>> formatProductInfo(List<dynamic> productInfo) async {
    return {
      'productName': productInfo[0],
      'manufacturer': productInfo[1],
      'expiryDate': productInfo[2],
    };
  }

  /// Function to format transfer information
  Future<Map<String, dynamic>> formatTransfer(List<dynamic> transfer) async {
    return {
      'transferTo': transfer[0],
      'date': transfer[1],
      'location': transfer[2],
    };
  }

  /// Main function to verify product and retrieve information from the blockchain
  Future<Map<String, dynamic>> verifyProduct(String productId, String serialNumber) async {
    try {
      final contract = await loadContract();

      // Get product info from the contract
      final productFunction = contract.function('getProductInfo');
      final productInfo = await web3client.call(
        contract: contract,
        function: productFunction,
        params: [productId, serialNumber],
      );

      final formattedProduct = await formatProductInfo(productInfo);

      // Get transfer history from the contract
      final transferFunction = contract.function('getTransferHistory');
      final transferHistory = await web3client.call(
        contract: contract,
        function: transferFunction,
        params: [productId, serialNumber],
      );

      final formattedTransfers = await Future.wait(transferHistory.map((transfer) async {
        return await formatTransfer(transfer);
      }).toList());

      return {
        'status': 'success',
        'product_info': formattedProduct,
        'transfer_history': formattedTransfers,
      };
    } catch (e) {
      return {
        'status': 'error',
        'message': e.toString(),
      };
    }
  }

  // Function to handle the product verification and display results
  Future<void> _verifyProduct() async {
    final String productId = _productIdController.text.trim();
    final String serialNumber = _serialNumberController.text.trim();

    if (productId.isEmpty || serialNumber.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter both Product ID and Serial Number.')),
      );
      return;
    }

    try {
      setState(() {
        isLoading = true;
      });

      final result = await verifyProduct(productId, serialNumber);

      if (result['status'] == 'success') {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Product verified successfully! Product Name: ${result['product_info']['productName']}')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Invalid product or serial number!')),
        );
      }
    } catch (error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error verifying product: $error')),
      );
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  // Function to open QR Scanner
  void _openQRScanner() async {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => QRScannerPage(
          onScanned: (result) {
            setState(() {
              _serialNumberController.text = result; // Set scanned value to the serial number controller
            });
          },
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Product Verification'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              'Product Verification',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 30),
            TextField(
              controller: _productIdController,
              decoration: const InputDecoration(
                labelText: 'Product ID',
                labelStyle: TextStyle(color: Colors.purple),
              ),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _serialNumberController,
              decoration: const InputDecoration(
                labelText: 'Serial Number',
                labelStyle: TextStyle(color: Colors.purple),
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: isLoading ? null : _verifyProduct,
              child: isLoading
                  ? CircularProgressIndicator()
                  : const Text('Verify Product'),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: _openQRScanner,
              icon: const Icon(Icons.qr_code_scanner),
              label: const Text('Scan QR Code'),
            ),
          ],
        ),
      ),
    );
  }
}

class QRScannerPage extends StatelessWidget {
  final Function(String) onScanned;

  const QRScannerPage({super.key, required this.onScanned});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('QR Scanner'),
      ),
      body: MobileScanner(
        onDetect: (barcodeCapture) {
          if (barcodeCapture.barcodes.isNotEmpty) {
            final String code = barcodeCapture.barcodes.first.rawValue ?? 'Unknown';
            Navigator.pop(context);
            onScanned(code);
          }
        },
      ),
    );
  }
}