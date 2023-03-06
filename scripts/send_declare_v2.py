"""Send a declare v2 tx"""

import json
import os

import requests
from starkware.crypto.signature.signature import sign
from starkware.starknet.core.os.contract_class.compiled_class_hash import (
    compute_compiled_class_hash,
)
from starkware.starknet.core.os.transaction_hash.transaction_hash import (
    calculate_declare_transaction_hash,
)
from starkware.starknet.definitions.general_config import StarknetChainId

import contract_class_utils

HOST = "https://external.integration.starknet.io"


def get_nonce(contract_address: str) -> int:
    """Accepts hex, returns int"""
    resp = requests.get(
        f"{HOST}/feeder_gateway/get_nonce?contractAddress={contract_address}"
    )
    hex_nonce = resp.json()
    return int(hex_nonce, 16)


def get_account():
    """Extract (address, private_key)"""
    home = os.path.expanduser("~")

    with open(
        f"{home}/.starknet_accounts/starknet_open_zeppelin_accounts.json",
        encoding="utf-8",
    ) as accounts_json:
        accounts = json.load(accounts_json)

    account = accounts["alpha-goerli"]["__default__"]
    return (
        int(account["address"], 16),
        int(account["private_key"], 16),
    )


def main():
    """Main method"""

    sender_address, private_key = get_account()

    artifacts_path = "test/artifacts/contracts/cairo1/contract.cairo"
    contract_class = contract_class_utils.load_sierra(f"{artifacts_path}/contract.json")
    compiled_class = contract_class_utils.load_casm(f"{artifacts_path}/contract.casm")

    compiled_class_hash = compute_compiled_class_hash(compiled_class)

    max_fee = int(1e18)  # should be enough
    version = 2
    nonce = get_nonce(hex(sender_address))
    chain_id = StarknetChainId.TESTNET.value
    hash_value = calculate_declare_transaction_hash(
        contract_class=contract_class,
        compiled_class_hash=compiled_class_hash,
        sender_address=sender_address,
        max_fee=max_fee,
        version=version,
        nonce=nonce,
        chain_id=chain_id,
    )
    signature = list(sign(msg_hash=hash_value, priv_key=private_key))

    declare_resp = requests.post(
        f"{HOST}/gateway/add_transaction",
        json={
            "version": hex(version),
            "max_fee": hex(max_fee),
            "signature": [hex(s) for s in signature],
            "nonce": hex(nonce),
            "contract_class": contract_class.dump(),
            "compiled_class_hash": hex(compiled_class_hash),
            "sender_address": hex(sender_address),
            "type": "DECLARE",
        },
    )

    print("Declare status code:", declare_resp.status_code)
    print("Declare response:", declare_resp.json())


if __name__ == "__main__":
    main()
