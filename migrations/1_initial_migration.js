const Migrations = artifacts.require("Migrations");
const PharmaSupplyChain = artifacts.require("PharmaSupplyChain");

module.exports = function(deployer) {
  deployer.deploy(Migrations);
  deployer.deploy(PharmaSupplyChain);
};