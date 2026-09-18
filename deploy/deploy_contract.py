import os
from pathlib import Path
from dotenv import load_dotenv
from solcx import compile_standard, install_solc
from web3 import Web3
import json

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / '.env')

INFURA_URL = os.getenv("INFURA_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT = os.getenv("ACCOUNT_ADDRESS")


def deploy_contract():
    """Deploy the CertRegistry contract"""

    if not INFURA_URL or not PRIVATE_KEY or not ACCOUNT:
        raise SystemExit(
            "❌ Set INFURA_URL, PRIVATE_KEY and ACCOUNT_ADDRESS in .env")

    print("🔨 Installing Solidity compiler...")
    install_solc('0.8.17')

    print("📖 Reading contract source...")
    contract_path = BASE / "contract" / "CertRegistry.sol"
    if not contract_path.exists():
        raise SystemExit(f"❌ Contract source not found at {contract_path}")

    source = contract_path.read_text()

    print("🔧 Compiling contract...")
    compiled = compile_standard({
        "language": "Solidity",
        "sources": {"CertRegistry.sol": {"content": source}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    }, solc_version="0.8.17")

    bytecode = compiled['contracts']['CertRegistry.sol']['CertRegistry']['evm']['bytecode']['object']
    abi = compiled['contracts']['CertRegistry.sol']['CertRegistry']['abi']

    print("🌐 Connecting to Sepolia network...")
    w3 = Web3(Web3.HTTPProvider(INFURA_URL))

    if not w3.is_connected():
        raise SystemExit("❌ Failed to connect to Ethereum network")

    chain_id = 11155111  # Sepolia
    acct = w3.to_checksum_address(ACCOUNT)

    # Check balance
    balance = w3.eth.get_balance(acct)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f"💰 Account balance: {balance_eth:.4f} ETH")

    if balance_eth < 0.01:
        print("⚠️  Low balance! Get test ETH from: https://sepolia-faucet.pk910.de/")

    print("🚀 Deploying contract...")
    Cert = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(acct)

    transaction = Cert.constructor().build_transaction({
        'chainId': chain_id,
        'from': acct,
        'nonce': nonce,
        'gas': 2000000,  # Reduced gas limit
        'gasPrice': w3.to_wei('20', 'gwei'),  # Reduced gas price
    })

    signed_txn = w3.eth.account.sign_transaction(
        transaction, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    tx_hash_hex = w3.to_hex(tx_hash)

    print(f"📤 Deploy transaction sent: {tx_hash_hex}")
    print("⏳ Waiting for confirmation...")

    try:
        tx_receipt = w3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=300)  # 5 minute timeout

        if tx_receipt.status == 1:
            contract_address = tx_receipt.contractAddress
            print(f"✅ Contract deployed successfully!")
            print(f"📍 Contract Address: {contract_address}")
            print(
                f"🔍 View on Etherscan: https://sepolia.etherscan.io/address/{contract_address}")

            # Save deployment info
            deploy_dir = BASE / "deploy"
            deploy_dir.mkdir(exist_ok=True)

            out_file = deploy_dir / "deployed_contract.json"
            deployment_data = {
                "address": contract_address,
                "abi": abi,
                "deployment_tx": tx_hash_hex,
                "deployment_block": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
                "network": "sepolia",
                "chain_id": chain_id
            }

            with open(out_file, 'w') as f:
                json.dump(deployment_data, f, indent=2)

            print(f"💾 Deployment info saved to {out_file}")

            return contract_address, abi

        else:
            raise SystemExit("❌ Contract deployment failed!")

    except Exception as e:
        print(f"❌ Deployment error: {e}")
        print(
            f"🔍 Check transaction: https://sepolia.etherscan.io/tx/{tx_hash_hex}")
        raise


if __name__ == "__main__":
    deploy_contract()
