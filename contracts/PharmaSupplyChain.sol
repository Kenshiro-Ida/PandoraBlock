// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PharmaSupplyChain {
    struct Product {
        string productId;
        string manufacturer;
        string batchNumber;
        uint256 manufactureDate;
        uint256 expiryDate;
        address currentOwner;
        string gtin;
        string serialNumber;
        bool exists;
    }
    
    struct Transfer {
        address from;
        address to;
        uint256 timestamp;
        string transferType;
    }
    
    // Product ID + Serial Number => Product
    mapping(bytes32 => Product) private products;
    
    // Product ID + Serial Number => Transfer History
    mapping(bytes32 => Transfer[]) private transferHistory;
    
    event ProductRegistered(
        string productId,
        string serialNumber,
        string manufacturer,
        uint256 timestamp
    );
    
    event ProductTransferred(
        string productId,
        string serialNumber,
        address from,
        address to,
        string transferType,
        uint256 timestamp
    );
    
    function getProductKey(string memory productId, string memory serialNumber) 
        private 
        pure 
        returns (bytes32) 
    {
        return keccak256(abi.encodePacked(productId, serialNumber));
    }
    
    function registerProduct(
        string memory productId,
        string memory manufacturer,
        string memory batchNumber,
        uint256 manufactureDate,
        uint256 expiryDate,
        string memory gtin,
        string memory serialNumber
    ) public {
        bytes32 productKey = getProductKey(productId, serialNumber);
        require(!products[productKey].exists, "Product already registered");
        
        products[productKey] = Product({
            productId: productId,
            manufacturer: manufacturer,
            batchNumber: batchNumber,
            manufactureDate: manufactureDate,
            expiryDate: expiryDate,
            currentOwner: msg.sender,
            gtin: gtin,
            serialNumber: serialNumber,
            exists: true
        });
        
        emit ProductRegistered(productId, serialNumber, manufacturer, block.timestamp);
    }
    
    function transferProduct(
        string memory productId,
        string memory serialNumber,
        address newOwner,
        string memory transferType
    ) public {
        bytes32 productKey = getProductKey(productId, serialNumber);
        require(products[productKey].exists, "Product does not exist");
        require(products[productKey].currentOwner == msg.sender, "Not authorized to transfer");
        
        address previousOwner = products[productKey].currentOwner;
        products[productKey].currentOwner = newOwner;
        
        transferHistory[productKey].push(Transfer({
            from: previousOwner,
            to: newOwner,
            timestamp: block.timestamp,
            transferType: transferType
        }));
        
        emit ProductTransferred(
            productId,
            serialNumber,
            previousOwner,
            newOwner,
            transferType,
            block.timestamp
        );
    }
    
    function getProductInfo(string memory productId, string memory serialNumber)
        public
        view
        returns (
            string memory,
            string memory,
            string memory,
            uint256,
            uint256,
            address,
            string memory,
            string memory
        )
    {
        bytes32 productKey = getProductKey(productId, serialNumber);
        require(products[productKey].exists, "Product does not exist");
        
        Product memory product = products[productKey];
        return (
            product.productId,
            product.manufacturer,
            product.batchNumber,
            product.manufactureDate,
            product.expiryDate,
            product.currentOwner,
            product.gtin,
            product.serialNumber
        );
    }
    
    function getTransferHistory(string memory productId, string memory serialNumber)
        public
        view
        returns (Transfer[] memory)
    {
        bytes32 productKey = getProductKey(productId, serialNumber);
        require(products[productKey].exists, "Product does not exist");
        
        return transferHistory[productKey];
    }
}