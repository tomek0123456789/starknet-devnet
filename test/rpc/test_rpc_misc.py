"""
Tests RPC miscellaneous
"""

from __future__ import annotations

from test.account import declare, invoke
from test.rpc.rpc_utils import deploy_and_invoke_storage_contract, rpc_call
from test.rpc.test_data.get_events import (
    BLOCK_FROM_0_TO_LATEST_MALFORMED_REQUEST,
    BLOCK_FROM_0_TO_LATEST_MISSING_PARAMETER,
    BLOCK_FROM_0_TO_LATEST_WRONG_BLOCK_TYPE,
    GET_EVENTS_TEST_DATA,
    create_get_events_rpc,
    create_block_from_0, BLOCK_FROM_0_TO_1_CHUNK_3_CONTINUATION_TOKEN,
)
from test.shared import (
    CONTRACT_PATH,
    DEPLOYER_CONTRACT_PATH,
    EVENTS_CONTRACT_PATH,
    EXPECTED_CLASS_HASH,
    EXPECTED_FEE_TOKEN_ADDRESS,
    PREDEPLOYED_ACCOUNT_ADDRESS,
    PREDEPLOYED_ACCOUNT_PRIVATE_KEY, PREDEPLOY_ACCOUNT_CLI_ARGS,
)
from test.test_account import deploy_empty_contract
from test.test_state_update import get_class_hash_at_path
from test.util import assert_hex_equal, assert_transaction, deploy

import pytest
from starkware.starknet.public.abi import get_storage_var_address

from starknet_devnet.blueprints.rpc.structures.types import PredefinedRpcErrorCode
from starknet_devnet.blueprints.rpc.utils import rpc_felt
from starknet_devnet.general_config import DEFAULT_GENERAL_CONFIG


@pytest.fixture(name="input_data")
def fixture_input_data(request):
    """
    Fixture for input data
    """
    return request.param


@pytest.fixture(name="expected_data")
def fixture_expected_data(request):
    """
    Fixture for return expected data
    """
    return request.param


@pytest.mark.usefixtures("devnet_with_account")
def test_get_state_update():
    """Test if declared classes successfully registered"""

    declare_info = declare(
        contract_path=CONTRACT_PATH,
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
        max_fee=int(4e16),
    )
    contract_class_hash = declare_info["class_hash"]
    assert_hex_equal(contract_class_hash, EXPECTED_CLASS_HASH)

    resp = rpc_call("starknet_getStateUpdate", params={"block_id": "latest"})
    diff_after_declare = resp["result"]["state_diff"]
    assert diff_after_declare["declared_contract_hashes"] == [
        rpc_felt(contract_class_hash)
    ]

    # Deploy the deployer - also deploys a contract of the declared class using the deploy syscall
    initial_balance_in_constructor = "5"
    deployer_deploy_info = deploy(
        contract=DEPLOYER_CONTRACT_PATH,
        inputs=[contract_class_hash, initial_balance_in_constructor],
    )
    deployer_class_hash = hex(get_class_hash_at_path(DEPLOYER_CONTRACT_PATH))
    deployer_address = deployer_deploy_info["address"]

    resp = rpc_call("starknet_getStateUpdate", params={"block_id": "latest"})
    diff_after_deploy = resp["result"]["state_diff"]

    deployer_diff = diff_after_deploy["deployed_contracts"][0]
    assert_hex_equal(deployer_diff["class_hash"], deployer_class_hash)
    assert_hex_equal(deployer_diff["address"], deployer_address)

    deployed_contract_diff = diff_after_deploy["deployed_contracts"][1]
    assert_hex_equal(deployed_contract_diff["class_hash"], contract_class_hash)
    # deployed_contract_diff["address"] is a random value

    # deployer expected to be declared
    assert diff_after_deploy["declared_contract_hashes"] == [
        rpc_felt(deployer_class_hash)
    ]


@pytest.mark.usefixtures("devnet_with_account")
def test_storage_diff():
    """Test storage diffs in the state update"""

    value = 30
    contract_address, _ = deploy_and_invoke_storage_contract(value)

    resp = rpc_call("starknet_getStateUpdate", params={"block_id": "latest"})
    storage_diffs = resp["result"]["state_diff"]["storage_diffs"]

    # list can be in different order per test run
    if storage_diffs[0]["address"] == rpc_felt(contract_address):
        storage_diffs[0], storage_diffs[1] = storage_diffs[1], storage_diffs[0]

    assert storage_diffs[0]["address"] == rpc_felt(EXPECTED_FEE_TOKEN_ADDRESS)
    assert storage_diffs[1] == {
        "address": rpc_felt(contract_address),
        "storage_entries": [
            {
                "key": rpc_felt(get_storage_var_address("storage")),
                "value": rpc_felt(value),
            }
        ],
    }


@pytest.mark.parametrize("params", [{}, None])
@pytest.mark.usefixtures("run_devnet_in_background")
def test_chain_id(params):
    """
    Test chain id
    """
    chain_id = DEFAULT_GENERAL_CONFIG.chain_id.value

    resp = rpc_call("starknet_chainId", params=params)
    rpc_chain_id = resp["result"]

    assert rpc_chain_id == hex(chain_id)


@pytest.mark.parametrize("params", [{}, None])
@pytest.mark.usefixtures("run_devnet_in_background")
def test_syncing(params):
    """
    Test syncing
    """
    resp = rpc_call("starknet_syncing", params=params)
    assert "result" in resp, f"Unexpected response: {resp}"

    result = resp["result"]
    assert result is False


@pytest.mark.usefixtures("run_devnet_in_background")
def test_call_method_with_incorrect_type_params():
    """Call with invalid params"""

    # could be any legal method, just passing something to get params to fail
    ex = rpc_call(method="starknet_getClass", params=1234)
    assert ex["error"] == {
        "code": -32602,
        "message": """Invalid "params" type. Value of "params" must be a dict or list""",
    }


@pytest.mark.usefixtures("run_devnet_in_background")
def test_get_events_malformed_request():
    """
    Test RPC get_events with malformed request.
    """
    resp = rpc_call(
        "starknet_getEvents",
        params=create_get_events_rpc(BLOCK_FROM_0_TO_LATEST_MALFORMED_REQUEST)[
            "params"
        ],
    )
    assert resp["error"]["code"] == PredefinedRpcErrorCode.INVALID_PARAMS.value


@pytest.mark.usefixtures("run_devnet_in_background")
def test_get_events_missing_parameter():
    """
    Test RPC get_events with malformed request.
    """
    resp = rpc_call(
        "starknet_getEvents",
        params=create_get_events_rpc(BLOCK_FROM_0_TO_LATEST_MISSING_PARAMETER)[
            "params"
        ],
    )
    assert resp["error"]["code"] == PredefinedRpcErrorCode.INVALID_PARAMS.value


@pytest.mark.usefixtures("run_devnet_in_background")
def test_get_events_wrong_blockid_type():
    """
    Test RPC get_events with malformed request.
    """
    resp = rpc_call(
        "starknet_getEvents",
        params=create_get_events_rpc(BLOCK_FROM_0_TO_LATEST_WRONG_BLOCK_TYPE)["params"],
    )
    assert resp["error"]["code"] == PredefinedRpcErrorCode.INVALID_PARAMS.value


@pytest.mark.usefixtures("run_devnet_in_background")
@pytest.mark.parametrize(
    "run_devnet_in_background",
    [PREDEPLOY_ACCOUNT_CLI_ARGS],
    indirect=True,
)
def test_get_events_continuation_token():
    """
    Test RPC get_events returning continuation token.
    """
    deploy_info = deploy(EVENTS_CONTRACT_PATH)
    for i in range(3):
        invoke(
            calls=[(deploy_info["address"], "increase_balance", [i])],
            account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
            private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
        )
    resp = rpc_call(
        "starknet_getEvents",
        params=create_get_events_rpc(create_block_from_0(3))["params"],
    )
    assert len(resp["result"]["events"]) == 3
    assert "continuation_token" not in resp["result"]

    resp = rpc_call(
        "starknet_getEvents",
        params=create_get_events_rpc(create_block_from_0(1))["params"],
    )
    assert len(resp["result"]["events"]) == 1
    assert resp["result"]["continuation_token"] == "1"

    resp = rpc_call(
        "starknet_getEvents",
        params=create_get_events_rpc(create_block_from_0(1, "1"))["params"],
    )
    assert len(resp["result"]["events"]) == 1
    assert resp["result"]["continuation_token"] == "2"

    resp = rpc_call(
        "starknet_getEvents",
        params=create_get_events_rpc(create_block_from_0(1, "2"))["params"],
    )
    assert len(resp["result"]["events"]) == 1
    assert "continuation_token" not in resp["result"]

    resp = rpc_call(
        "starknet_getEvents",
        params=create_get_events_rpc(BLOCK_FROM_0_TO_1_CHUNK_3_CONTINUATION_TOKEN)["params"],
    )
    assert len(resp["result"]["events"]) == 0
    assert "continuation_token" not in resp["result"]


@pytest.mark.usefixtures("run_devnet_in_background")
@pytest.mark.parametrize(
    "run_devnet_in_background, input_data, expected_data",
    GET_EVENTS_TEST_DATA,
    indirect=True,
)
def test_get_events(input_data, expected_data):
    """
    Test RPC get_events.
    """
    deploy_info = deploy(EVENTS_CONTRACT_PATH)
    for i in range(2):
        invoke(
            calls=[(deploy_info["address"], "increase_balance", [i])],
            account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
            private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
        )
    resp = rpc_call("starknet_getEvents", params=input_data["params"])
    assert len(expected_data) == len(resp["result"]["events"])
    for i, data in enumerate(expected_data):
        assert resp["result"]["events"][i]["data"] == data


@pytest.mark.usefixtures("devnet_with_account")
def test_get_nonce():
    """Test get_nonce"""

    account_address = PREDEPLOYED_ACCOUNT_ADDRESS

    initial_resp = rpc_call(
        method="starknet_getNonce",
        params={"block_id": "latest", "contract_address": rpc_felt(account_address)},
    )
    assert initial_resp["result"] == "0x00"

    deployment_info = deploy_empty_contract()

    invoke_tx_hash = invoke(
        calls=[(deployment_info["address"], "increase_balance", [10, 20])],
        account_address=account_address,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    )
    assert_transaction(invoke_tx_hash, "ACCEPTED_ON_L2")

    final_resp = rpc_call(
        method="starknet_getNonce",
        params={"block_id": "latest", "contract_address": rpc_felt(account_address)},
    )
    assert final_resp["result"] == "0x01"


@pytest.mark.usefixtures("devnet_with_account")
def test_get_nonce_invalid_address():
    """Test get_nonce with invalid address"""

    account_address = "0x1111"

    ex = rpc_call(
        method="starknet_getNonce",
        params={"block_id": "latest", "contract_address": rpc_felt(account_address)},
    )
    assert ex["error"] == {"code": 20, "message": "Contract not found"}
