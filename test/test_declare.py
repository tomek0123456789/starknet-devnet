"""
Tests of contract class declaration and deploy syscall.
"""

import pytest
import requests
from starkware.crypto.signature.signature import sign
from starkware.starknet.core.os.contract_class.compiled_class_hash import (
    compute_compiled_class_hash,
)
from starkware.starknet.core.os.transaction_hash.transaction_hash import (
    calculate_declare_transaction_hash,
)
from starkware.starknet.definitions.error_codes import StarknetErrorCode
from starkware.starknet.definitions.general_config import StarknetChainId
from starkware.starknet.services.api.contract_class.contract_class import (
    CompiledClass,
    ContractClass,
)
from starkware.starknet.services.api.contract_class.contract_class_utils import (
    load_sierra,
)
from starkware.starknet.services.api.gateway.transaction import Declare

from .account import declare, deploy, get_nonce, invoke
from .settings import APP_URL
from .shared import (
    ABI_1_PATH,
    CONTRACT_1_CASM_PATH,
    CONTRACT_1_PATH,
    CONTRACT_PATH,
    EXPECTED_CLASS_HASH,
    PREDEPLOY_ACCOUNT_CLI_ARGS,
    PREDEPLOYED_ACCOUNT_ADDRESS,
    PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
)
from .util import (
    assert_class_by_hash,
    assert_hex_equal,
    assert_tx_status,
    call,
    devnet_in_background,
    get_class_by_hash,
    get_compiled_class_by_class_hash,
)


@pytest.mark.declare
@devnet_in_background(*PREDEPLOY_ACCOUNT_CLI_ARGS)
def test_declare_max_fee_too_low():
    """Test declaring if max fee too low"""

    declare_info = declare(
        contract_path=CONTRACT_PATH,
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
        max_fee=1,
    )
    class_hash = declare_info["class_hash"]
    assert_hex_equal(class_hash, EXPECTED_CLASS_HASH)
    assert_tx_status(declare_info["tx_hash"], "REJECTED")

    resp = requests.get(
        f"{APP_URL}/feeder_gateway/get_class_by_hash?classHash={class_hash}"
    )
    assert resp.json()["code"] == str(StarknetErrorCode.UNDECLARED_CLASS)
    assert resp.status_code == 500


@pytest.mark.declare
@devnet_in_background(*PREDEPLOY_ACCOUNT_CLI_ARGS)
def test_declare_happy_path():
    """Test declaring if max fee sufficient"""

    declare_info = declare(
        contract_path=CONTRACT_PATH,
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
        max_fee=int(1e18),
    )
    class_hash = declare_info["class_hash"]
    assert_hex_equal(class_hash, EXPECTED_CLASS_HASH)
    assert_tx_status(declare_info["tx_hash"], "ACCEPTED_ON_L2")
    assert_class_by_hash(class_hash, CONTRACT_PATH)

    _assert_undeclared_class(
        resp=get_compiled_class_by_class_hash(class_hash)
    )


def _assert_undeclared_class(resp=requests.Response):
    assert resp.status_code == 500, resp.json()
    resp_body = resp.json()
    assert "code" in resp_body
    assert resp_body["code"] == str(StarknetErrorCode.UNDECLARED_CLASS)


def _assert_declare_v2(
    resp: requests.Response,
    contract_class: ContractClass,
    compiled_class: CompiledClass,
    compiled_class_hash: int,
):
    assert resp.status_code == 200

    class_hash = resp.json()["class_hash"]
    declare_tx_hash = resp.json()["transaction_hash"]
    assert_tx_status(tx_hash=declare_tx_hash, expected_tx_status="ACCEPTED_ON_L2")

    # assert class present only by class hash
    assert ContractClass.load(get_class_by_hash(class_hash).json()) == contract_class
    _assert_undeclared_class(
        resp=get_class_by_hash(class_hash=hex(compiled_class_hash))
    )

    # assert compiled class present only by class hash
    assert (
        CompiledClass.load(get_compiled_class_by_class_hash(class_hash).json())
        == compiled_class
    )
    _assert_undeclared_class(
        resp=get_compiled_class_by_class_hash(hex(compiled_class_hash))
    )

    # assert class present in state update
    # TODO in another test assert only old contract classes populated (not declared classes)


def _declare_v2(
    contract_class_path: str,
    compiled_class_path: str,
    sender_address: str,
    sender_key: int,
):
    contract_class = load_sierra(contract_class_path)
    with open(compiled_class_path, encoding="utf-8") as casm_file:
        compiled_class = CompiledClass.loads(casm_file.read())

    compiled_class_hash = compute_compiled_class_hash(compiled_class)

    max_fee = int(1e18)  # should be enough
    version = 2
    nonce = get_nonce(sender_address)
    chain_id = StarknetChainId.TESTNET.value
    hash_value = calculate_declare_transaction_hash(
        contract_class=contract_class,
        compiled_class_hash=compiled_class_hash,
        sender_address=int(sender_address, 16),
        max_fee=max_fee,
        version=version,
        nonce=nonce,
        chain_id=chain_id,
    )

    declaration_body = Declare(
        contract_class=contract_class,
        compiled_class_hash=compiled_class_hash,
        sender_address=int(sender_address, 16),
        version=version,
        max_fee=max_fee,
        signature=list(sign(msg_hash=hash_value, priv_key=sender_key)),
        nonce=nonce,
    ).dump()
    declaration_body["type"] = "DECLARE"

    resp = requests.post(f"{APP_URL}/gateway/add_transaction", json=declaration_body)
    _assert_declare_v2(
        resp=resp,
        contract_class=contract_class,
        compiled_class=compiled_class,
        compiled_class_hash=compiled_class_hash,
    )
    return resp.json()["class_hash"]


def _call_get_balance(address: str) -> int:
    balance = call(
        function="get_balance",
        address=address,
        abi_path=ABI_1_PATH,
    )
    return int(balance, base=10)


@pytest.mark.declare
@devnet_in_background(*PREDEPLOY_ACCOUNT_CLI_ARGS)
def test_declare_v2_happy_path():
    """Test declare v2"""

    # declare
    class_hash = _declare_v2(
        contract_class_path=CONTRACT_1_PATH,
        compiled_class_path=CONTRACT_1_CASM_PATH,
        sender_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        sender_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    )

    # deploy
    initial_balance = 10
    deploy_info = deploy(
        class_hash=class_hash,
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
        inputs=[str(initial_balance)],
        max_fee=int(1e18),
    )
    assert_tx_status(
        tx_hash=deploy_info["tx_hash"], expected_tx_status="ACCEPTED_ON_L2"
    )

    # call after deployment
    initial_fetched_balance = _call_get_balance(deploy_info["address"])
    assert initial_fetched_balance == initial_balance

    # invoke
    increment_value = 15
    invoke_tx_hash = invoke(
        calls=[(deploy_info["address"], "increase_balance", [increment_value, 0])],
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    )
    assert_tx_status(tx_hash=invoke_tx_hash, expected_tx_status="ACCEPTED_ON_L2")

    # call after invoke
    fetched_balance_after_invoke = _call_get_balance(deploy_info["address"])
    assert fetched_balance_after_invoke == initial_balance + increment_value
