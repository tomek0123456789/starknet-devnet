"""
Tests the general workflow of the devnet.
"""

import pytest

from .account import invoke
from .shared import (
    ABI_PATH,
    BALANCE_KEY,
    CONTRACT_PATH,
    EVENTS_CONTRACT_PATH,
    EXPECTED_SALTY_DEPLOY_ADDRESS,
    EXPECTED_SALTY_DEPLOY_HASH,
    FAILING_CONTRACT_PATH,
    GENESIS_BLOCK_NUMBER,
    NONEXISTENT_TX_HASH,
    PREDEPLOY_ACCOUNT_CLI_ARGS,
    PREDEPLOYED_ACCOUNT_ADDRESS,
    PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
)
from .util import (
    assert_block,
    assert_class_by_hash,
    assert_contract_code_present,
    assert_equal,
    assert_events,
    assert_full_contract,
    assert_negative_block_input,
    assert_receipt,
    assert_salty_deploy,
    assert_storage,
    assert_transaction,
    assert_transaction_not_received,
    assert_transaction_receipt_not_received,
    assert_tx_status,
    call,
    deploy,
    get_block,
    get_class_hash_at,
)

EXPECTED_SALTY_DEPLOY_BLOCK_HASH_LITE_MODE = "0x1"


def _assert_failing_deploy(contract_path):
    """Run deployment for a contract that's expected to be rejected."""
    deploy_info = deploy(contract_path)
    assert_tx_status(deploy_info["tx_hash"], "REJECTED")
    assert_transaction(deploy_info["tx_hash"], "REJECTED")


@pytest.mark.usefixtures("run_devnet_in_background")
@pytest.mark.parametrize(
    "run_devnet_in_background, expected_block_hash",
    [
        (
            [*PREDEPLOY_ACCOUNT_CLI_ARGS],
            "",
        ),
        (
            [*PREDEPLOY_ACCOUNT_CLI_ARGS, "--lite-mode"],
            EXPECTED_SALTY_DEPLOY_BLOCK_HASH_LITE_MODE,
        ),
    ],
    indirect=True,
)
def test_general_workflow(expected_block_hash):
    """Test devnet with CLI"""
    deploy_info = deploy(CONTRACT_PATH, inputs=["0"])

    assert_tx_status(deploy_info["tx_hash"], "ACCEPTED_ON_L2")
    assert_transaction(deploy_info["tx_hash"], "ACCEPTED_ON_L2")
    assert_transaction_not_received(NONEXISTENT_TX_HASH)

    # check storage after deployment
    assert_storage(deploy_info["address"], BALANCE_KEY, "0x0")

    # check block and receipt after deployment
    assert_negative_block_input()

    # check if in lite mode expected block hash is 0x1
    if expected_block_hash == EXPECTED_SALTY_DEPLOY_BLOCK_HASH_LITE_MODE:
        assert_equal(expected_block_hash, get_block(parse=True)["block_hash"])

    assert_block(GENESIS_BLOCK_NUMBER + 1, deploy_info["tx_hash"])
    assert_receipt(deploy_info["tx_hash"], "test/expected/deploy_receipt.json")
    assert_transaction_receipt_not_received(NONEXISTENT_TX_HASH)

    # check code
    assert_contract_code_present(deploy_info["address"])

    # check contract class
    assert_full_contract(address=deploy_info["address"], expected_path=CONTRACT_PATH)

    # check contract class through class hash
    class_hash = get_class_hash_at(deploy_info["address"])
    assert_class_by_hash(class_hash, expected_path=CONTRACT_PATH)

    # increase and assert balance
    invoke_tx_hash = invoke(
        calls=[(deploy_info["address"], "increase_balance", [10, 20])],
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    )
    assert_transaction(invoke_tx_hash, "ACCEPTED_ON_L2")
    value = call(
        function="get_balance", address=deploy_info["address"], abi_path=ABI_PATH
    )
    assert_equal(value, "30", "Invoke+call failed!")

    # check storage, block and receipt after increase
    assert_storage(deploy_info["address"], BALANCE_KEY, "0x1e")
    assert_block(GENESIS_BLOCK_NUMBER + 2, invoke_tx_hash)
    assert_receipt(invoke_tx_hash, "test/expected/invoke_receipt.json")

    # check handling complex input
    value = call(
        function="sum_point_array",
        address=deploy_info["address"],
        abi_path=ABI_PATH,
        inputs=["2", "10", "20", "30", "40"],
    )
    assert_equal(value, "40 60", "Checking complex input failed!")

    # check deploy when a salt is provided, and use the same contract to test events
    for _ in range(2):
        assert_salty_deploy(
            contract_path=EVENTS_CONTRACT_PATH,
            salt="0x99",
            inputs=None,
            expected_status="ACCEPTED_ON_L2",
            expected_address=EXPECTED_SALTY_DEPLOY_ADDRESS,
            expected_tx_hash=EXPECTED_SALTY_DEPLOY_HASH,
        )

    salty_invoke_tx_hash = invoke(
        calls=[(EXPECTED_SALTY_DEPLOY_ADDRESS, "increase_balance", [10])],
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    )

    assert_events(salty_invoke_tx_hash, "test/expected/invoke_receipt_event.json")

    _assert_failing_deploy(contract_path=FAILING_CONTRACT_PATH)
