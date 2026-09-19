const hre = require("hardhat");

async function main() {
  const CertRegistry = await hre.ethers.getContractFactory("CertRegistry");
  const certRegistry = await CertRegistry.deploy();
  await certRegistry.waitForDeployment();

  const address = await certRegistry.getAddress();
  console.log("CertRegistry deployed to:", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
