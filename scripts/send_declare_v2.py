"""Send a declare v2 tx"""

import os
import sys

import requests
from starkware.crypto.signature.signature import sign
from starkware.starknet.core.os.contract_class.compiled_class_hash import (
    compute_compiled_class_hash,
)
from starkware.starknet.core.os.transaction_hash.transaction_hash import (
    calculate_declare_transaction_hash,
    compute_class_hash,
)
from starkware.starknet.definitions.general_config import StarknetChainId
from starkware.starknet.services.api.contract_class.contract_class import CompiledClass
from starkware.starknet.services.api.contract_class.contract_class_utils import (
    load_sierra,
)
from starkware.starknet.services.api.gateway.transaction import Declare


def _get_env_var(var_name: str):
    try:
        return os.environ[var_name]
    except KeyError:
        sys.exit(f"Error: Please provide env var {var_name}")


HOST = _get_env_var("HOST")


def get_nonce(contract_address: str) -> int:
    """Accepts hex, returns int"""
    resp = requests.get(
        f"{HOST}/feeder_gateway/get_nonce?contractAddress={contract_address}"
    )
    hex_nonce = resp.json()
    return int(hex_nonce, 16)


def get_account():
    """Extract (address, private_key)"""
    return (
        int(_get_env_var("ACCOUNT_ADDRESS"), 16),
        int(_get_env_var("ACCOUNT_PRIVATE_KEY"), 16),
    )


def _get_class(class_hash: int):
    class_hash = hex(class_hash)
    print("Getting class for", class_hash)
    resp = requests.get(
        f"{HOST}/feeder_gateway/get_class_by_hash",
        params={"classHash": class_hash},
    )
    print("Get class status_code:", resp.status_code)
    print(
        "Get class response:",
        str(resp.json())[:100] if resp.status_code == 200 else resp.json(),
    )


def _get_compiled_class(class_hash: int):
    class_hash = hex(class_hash)
    print("Getting compiled class for", class_hash)
    resp = requests.get(
        f"{HOST}/feeder_gateway/get_compiled_class_by_class_hash",
        params={"classHash": class_hash},
    )
    print("Get class status_code:", resp.status_code)
    print(
        "Get class response:",
        str(resp.json())[:100] if resp.status_code == 200 else resp.json(),
    )


def _get_transaction(transaction_hash: str):
    resp = requests.get(
        f"{HOST}/feeder_gateway/get_transaction",
        params={"transactionHash": transaction_hash},
    )
    print("Get transaction status_code:", resp.status_code)
    print("Get transaction response:", resp.json())


def _get_transaction_receipt(transaction_hash: str):
    resp = requests.get(
        f"{HOST}/feeder_gateway/get_transaction_receipt",
        params={"transactionHash": transaction_hash},
    )
    print("Get transaction receipt status_code:", resp.status_code)
    print("Get transaction receipt response:", resp.json())


def main():  # pylint: disable=too-many-locals
    """Main method"""

    print("Sending request to:", HOST)

    sender_address, private_key = get_account()

    artifacts_path = "test/artifacts/contracts/cairo1/contract.cairo"
    contract_class = load_sierra(f"{artifacts_path}/contract.json")
    with open(f"{artifacts_path}/contract.casm", encoding="utf-8") as casm_file:
        compiled_class = CompiledClass.loads(casm_file.read())

    class_hash = compute_class_hash(contract_class)
    print("Class hash:", hex(class_hash))
    compiled_class_hash = compute_compiled_class_hash(compiled_class)
    print("Compiled class hash:", hex(compiled_class_hash))

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

    declaration_body = Declare(
        contract_class=contract_class,
        compiled_class_hash=compiled_class_hash,
        sender_address=sender_address,
        version=version,
        max_fee=max_fee,
        signature=list(sign(msg_hash=hash_value, priv_key=private_key)),
        nonce=nonce,
    ).dump()

    declaration_body["type"] = "DECLARE"

    declare_resp = requests.post(
        f"{HOST}/gateway/add_transaction", json=declaration_body
    )
    assert declare_resp.status_code == 200, declare_resp.json()
    print("Declare response:", declare_resp.json())
    tx_hash = declare_resp.json()["transaction_hash"]

    print("\nGetting class")
    _get_class(class_hash)
    _get_class(compiled_class_hash)

    print("\nGetting compiled class")
    _get_compiled_class(class_hash)
    _get_compiled_class(compiled_class_hash)

    print("\nGetting tx info")
    _get_transaction(tx_hash)
    _get_transaction_receipt(tx_hash)


if __name__ == "__main__":
    main()
