import hashlib
import json
import os
from dotenv import load_dotenv
from web3 import Web3

# Load environment variables
load_dotenv()

WEB3_PROVIDER_URL = os.getenv("WEB3_PROVIDER_URL", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ISSUER_ADDRESS = os.getenv("ISSUER_ADDRESS")

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))

# Load Contract ABI
ABI_FILE_PATH = os.path.join(os.path.dirname(__file__), "contract_abi.json")
with open(ABI_FILE_PATH, "r") as f:
    contract_abi = json.load(f)

# Initialize Contract Instance
if CONTRACT_ADDRESS:
    contract_address_checksum = w3.to_checksum_address(CONTRACT_ADDRESS)
    badge_contract = w3.eth.contract(address=contract_address_checksum, abi=contract_abi)
else:
    badge_contract = None


def generate_badge_hash(badge_assertion: dict) -> bytes:
    """
    Computes a deterministic SHA-256 hash (32 bytes) of assertion metadata.
    Uses strict separators to eliminate JSON whitespace variations.
    """
    assertion_json = json.dumps(badge_assertion, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(assertion_json.encode("utf-8")).digest()


def anchor_badge_on_chain(badge_id: str, badge_assertion: dict) -> str:
    """
    Signs and sends an Ethereum transaction to record the badge hash on-chain.
    Returns the transaction hash string.
    """
    if not badge_contract:
        raise ValueError("CONTRACT_ADDRESS is not set in environment variables.")

    if not w3.is_connected():
        raise ConnectionError("Failed to connect to local Web3 RPC provider.")

    badge_hash = generate_badge_hash(badge_assertion)
    account_address = w3.to_checksum_address(ISSUER_ADDRESS)

    # Build transaction
    nonce = w3.eth.get_transaction_count(account_address)
    tx = badge_contract.functions.issueBadge(badge_id, badge_hash).build_transaction({
        "from": account_address,
        "nonce": nonce,
        "gas": 300000,
        "gasPrice": w3.eth.gas_price,
    })

    # Sign transaction with private key
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)

    # Send raw transaction
    tx_hash_bytes = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash_bytes)

    return tx_receipt["transactionHash"].hex()


def verify_badge_on_chain(badge_id: str, badge_assertion: dict) -> dict:
    try:
        if not badge_contract:
            return {
                "badge_id": badge_id,
                "is_valid": False,
                "error": "CONTRACT_ADDRESS is not set in environment variables.",
                "computed_hash": None
            }

        badge_hash = generate_badge_hash(badge_assertion)
        computed_hex = w3.to_hex(badge_hash).lower()

        on_chain_hash_bytes, issuer, timestamp = badge_contract.functions.verifyBadge(badge_id).call()
        on_chain_hex = w3.to_hex(on_chain_hash_bytes).lower()

        is_valid = (on_chain_hex == computed_hex)

        # Print debug comparison directly to terminal
        print("\n=== DEBUG BLOCKCHAIN VERIFICATION ===")
        print(f"Badge ID:       {badge_id}")
        print(f"On-Chain Hash:  {on_chain_hex}")
        print(f"Computed Hash:  {computed_hex}")
        print(f"Hashes Match:   {is_valid}")
        print("=====================================\n")

        return {
            "badge_id": badge_id,
            "is_valid": is_valid,
            "on_chain_hash": on_chain_hex,
            "computed_hash": computed_hex,
            "issuer": issuer,
            "block_timestamp": timestamp
        }
    except Exception as e:
        print(f"\n[DEBUG ERROR] Verification failed: {str(e)}\n")
        return {
            "badge_id": badge_id,
            "is_valid": False,
            "error": f"Verification call failed: {str(e)}",
            "computed_hash": locals().get('computed_hex', None)
        }