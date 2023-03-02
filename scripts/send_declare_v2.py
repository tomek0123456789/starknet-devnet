"""Send a declare v2 tx"""

import json
import os
from typing import Dict

import requests
from starkware.crypto.signature.signature import sign
from starkware.starknet.core.os.contract_class.compiled_class_hash import (
    compute_compiled_class_hash,
)
from starkware.starknet.core.os.transaction_hash.transaction_hash import (
    calculate_declare_transaction_hash,
)
from starkware.starknet.definitions.general_config import StarknetChainId
from starkware.starknet.services.api.contract_class.contract_class import (
    CompiledClass,
    ContractClass,
)

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


def load_contract_class(artifact_path: str) -> CompiledClass:
    """Load contract class"""
    with open(artifact_path, encoding="utf-8") as sierra_file:
        contract_class_dict = json.load(sierra_file)

    del contract_class_dict["sierra_program_debug_info"]
    contract_class_dict["abi"] = json.dumps(contract_class_dict["abi"])
    return ContractClass.load(contract_class_dict)


def load_compiled_class(artifact_path: str) -> CompiledClass:
    """Load casm"""
    with open(artifact_path, encoding="utf-8") as casm_file:
        casm_dict: Dict = json.load(casm_file)

    entry_points_by_type = casm_dict["entry_points_by_type"]
    builtins = []  # seems that all builtins need to be reported separately
    for _, entry_points in entry_points_by_type.items():
        for entry_point in entry_points:
            # fix foramt of offset to hex
            entry_point["offset"] = hex(entry_point["offset"])
            builtins.extend(entry_point["builtins"])

    return CompiledClass.load(
        {
            "program": {
                "prime": casm_dict["prime"],
                "data": casm_dict["bytecode"],
                "builtins": builtins,  # TODO
                "hints": dict(casm_dict["hints"]),
                "compiler_version": casm_dict["compiler_version"],
            },
            "entry_points_by_type": entry_points_by_type,
        }
    )


def main():
    """Main method"""

    sender_address, private_key = get_account()

    artifacts_path = "test/artifacts/contracts/cairo1/contract.cairo"
    contract_class = load_contract_class(f"{artifacts_path}/contract.json")
    compiled_class = load_compiled_class(f"{artifacts_path}/contract.casm")

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
