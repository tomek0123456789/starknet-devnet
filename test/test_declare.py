"""
Tests of contract class declaration and deploy syscall.
"""

import pytest
import requests
from starkware.starknet.core.os.contract_class.compiled_class_hash import (
    compute_compiled_class_hash,
)

from starkware.starknet.definitions.error_codes import StarknetErrorCode
from starkware.starknet.services.api.contract_class.contract_class import (
    CompiledClass,
    ContractClass,
)
from starkware.starknet.services.api.contract_class.contract_class_utils import (
    load_sierra,
)

from .account import declare, send_declare_v2, deploy, invoke
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
from .test_state_update import get_state_update
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

    _assert_undeclared_class(resp=get_compiled_class_by_class_hash(class_hash))


def _assert_undeclared_class(resp=requests.Response):
    assert resp.status_code == 500, resp.json()
    resp_body = resp.json()
    assert "code" in resp_body
    assert resp_body["code"] == str(StarknetErrorCode.UNDECLARED_CLASS)


def _assert_declare_v2_accepted(
    resp: requests.Response,
):
    assert resp.status_code == 200

    declare_tx_hash = resp.json()["transaction_hash"]
    assert_tx_status(tx_hash=declare_tx_hash, expected_tx_status="ACCEPTED_ON_L2")


def _assert_already_declared(declaration_resp: requests.Response):
    assert declaration_resp.status_code == 200, declaration_resp.json()
    declare_tx_hash = declaration_resp.json()["transaction_hash"]

    tx_resp = requests.get(
        f"{APP_URL}/feeder_gateway/get_transaction",
        params={"transactionHash": declare_tx_hash},
    )
    assert tx_resp.status_code == 200, tx_resp.json()
    tx_resp_body = tx_resp.json()

    assert tx_resp_body.get("status") == "REJECTED", tx_resp_body
    assert (
        "already declared"
        in tx_resp_body["transaction_failure_reason"]["error_message"]
    )


def _assert_invalid_compiled_class_hash(declaration_resp: requests.Response):
    assert declaration_resp.status_code == 200, declaration_resp.json()
    declare_tx_hash = declaration_resp.json()["transaction_hash"]

    tx_resp = requests.get(
        f"{APP_URL}/feeder_gateway/get_transaction",
        params={"transactionHash": declare_tx_hash},
    )
    assert tx_resp.status_code == 200, tx_resp.json()
    tx_resp_body = tx_resp.json()

    assert tx_resp_body.get("status") == "REJECTED", tx_resp_body
    assert (
        "Compiled class hash not matching"
        in tx_resp_body["transaction_failure_reason"]["error_message"]
    )


def _load_cairo1_contract():
    contract_class = load_sierra(CONTRACT_1_PATH)
    with open(CONTRACT_1_CASM_PATH, encoding="utf-8") as casm_file:
        compiled_class = CompiledClass.loads(casm_file.read())
    compiled_class_hash = compute_compiled_class_hash(compiled_class)

    return contract_class, compiled_class, compiled_class_hash


@pytest.mark.declare
@devnet_in_background(*PREDEPLOY_ACCOUNT_CLI_ARGS)
def test_declare_v2_invalid_compiled_class_hash():
    """Set an invalid compiled class hash and expect failure"""
    contract_class, _, compiled_class_hash = _load_cairo1_contract()
    _assert_invalid_compiled_class_hash(
        send_declare_v2(
            contract_class=contract_class,
            # invalid compiled class hash
            compiled_class_hash=compiled_class_hash + 1,
            sender_address=PREDEPLOYED_ACCOUNT_ADDRESS,
            sender_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
        )
    )


@pytest.mark.declare
@devnet_in_background(*PREDEPLOY_ACCOUNT_CLI_ARGS)
def test_redeclaring_v2():
    """Should fail if redeclaring"""
    contract_class, _, compiled_class_hash = _load_cairo1_contract()
    send_declare_v2(
        contract_class=contract_class,
        compiled_class_hash=compiled_class_hash,
        sender_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        sender_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    )

    _assert_already_declared(
        send_declare_v2(
            contract_class=contract_class,
            compiled_class_hash=compiled_class_hash,
            sender_address=PREDEPLOYED_ACCOUNT_ADDRESS,
            sender_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
        )
    )


@pytest.mark.declare
@devnet_in_background(*PREDEPLOY_ACCOUNT_CLI_ARGS)
def test_classes_available_after_declare_v2():
    """Should successfully get class and compiled class by hash"""
    # assert class present only by class hash

    contract_class, compiled_class, compiled_class_hash = _load_cairo1_contract()

    declaration_resp = send_declare_v2(
        contract_class=contract_class,
        compiled_class_hash=compiled_class_hash,
        sender_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        sender_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    )
    _assert_declare_v2_accepted(declaration_resp)
    class_hash = declaration_resp.json()["class_hash"]

    assert ContractClass.load(get_class_by_hash(class_hash).json()) == contract_class
    _assert_undeclared_class(
        resp=get_class_by_hash(class_hash=hex(compiled_class_hash))
    )

    # assert compiled class retrievable only by class hash
    assert (
        CompiledClass.load(get_compiled_class_by_class_hash(class_hash).json())
        == compiled_class
    )
    _assert_undeclared_class(
        resp=get_compiled_class_by_class_hash(hex(compiled_class_hash))
    )

    # assert class present in the right property of state update
    state_update = get_state_update()
    assert "state_diff" in state_update

    assert state_update["state_diff"]["old_declared_contracts"] == []
    declared_classes = state_update["state_diff"]["declared_classes"]
    assert len(declared_classes) == 1
    assert_hex_equal(declared_classes[0]["class_hash"], class_hash)
    assert_hex_equal(
        declared_classes[0]["compiled_class_hash"], hex(compiled_class_hash)
    )


def _call_get_balance(address: str) -> int:
    balance = call(
        function="get_balance",
        address=address,
        abi_path=ABI_1_PATH,
    )
    return int(balance, base=10)


@pytest.mark.declare
@devnet_in_background(*PREDEPLOY_ACCOUNT_CLI_ARGS)
def test_v2_contract_interaction():
    """Test using declare v2 and interact with contract (deploy, invoke, call)"""

    contract_class, _, compiled_class_hash = _load_cairo1_contract()

    # declare
    declaration_resp = send_declare_v2(
        contract_class=contract_class,
        compiled_class_hash=compiled_class_hash,
        sender_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        sender_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    )
    _assert_declare_v2_accepted(declaration_resp)
    class_hash = declaration_resp.json()["class_hash"]

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
