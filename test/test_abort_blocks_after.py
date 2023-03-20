"""
Tests the abort block functionality.
"""

import pytest
import requests

from .account import invoke
from .settings import APP_URL
from .shared import (
    CONTRACT_PATH,
    PREDEPLOY_ACCOUNT_CLI_ARGS,
    PREDEPLOYED_ACCOUNT_ADDRESS,
    PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
)
from .util import (
    assert_transaction,
    assert_tx_status,
    deploy,
    devnet_in_background,
    get_block,
)

EXPECTED_ABORT_HASHES = ["0x1", "0x2"]
NOT_EXISTING_BLOCK = "0x9"


def abort_blocks_after(block_hash):
    """Abort blocks after certain block hash"""
    return requests.post(
        f"{APP_URL}/abort_blocks_after", json={"blockHash": block_hash}
    )


@devnet_in_background()
def test_abort_not_existing_block():
    response = abort_blocks_after(NOT_EXISTING_BLOCK)
    assert response.status_code == 500


@devnet_in_background()
def test_abort_single_block_single_transaction():
    """Test abort of single block and single transaction."""

    # Contract deploy block should be accepted on L2 and
    # transaction should be accepted on L2
    contract_deploy_info = deploy(CONTRACT_PATH, inputs=["0"])
    contract_deploy_block = get_block(parse=True)
    assert contract_deploy_block["status"] == "ACCEPTED_ON_L2"
    assert_tx_status(contract_deploy_info["tx_hash"], "ACCEPTED_ON_L2")

    # After abort blocks call block should be aborted and
    # transaction should be rejected
    response = abort_blocks_after(contract_deploy_block["block_hash"])
    contract_deploy_block_after_abort = get_block(parse=True)
    assert response.status_code == 200
    assert contract_deploy_block_after_abort["status"] == "ABORTED"
    assert_transaction(contract_deploy_info["tx_hash"], "REJECTED")


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
            EXPECTED_ABORT_HASHES,
        ),
    ],
    indirect=True,
)
def test_abort_many_blocks_many_transactions(expected_block_hash):
    """Test abort of many blocks and many transactions."""

    # Contract deploy block should be accepted on L2 and
    # transaction should be accepted on L2
    contract_deploy_info = deploy(CONTRACT_PATH, inputs=["0"])
    contract_deploy_block = get_block(parse=True)
    assert contract_deploy_block["status"] == "ACCEPTED_ON_L2"
    assert_tx_status(contract_deploy_info["tx_hash"], "ACCEPTED_ON_L2")

    # Increase balance block should be accepted on L2 and
    # transaction should be accepted on L2
    invoke_tx_hash = invoke(
        calls=[(contract_deploy_info["address"], "increase_balance", [10, 20])],
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    )
    invoke_block = get_block(parse=True)
    assert invoke_block["status"] == "ACCEPTED_ON_L2"
    assert_transaction(invoke_tx_hash, "ACCEPTED_ON_L2")

    # After abort blocks call blocks should be aborted and
    # transactions should be rejected
    response = abort_blocks_after(contract_deploy_block["block_hash"])
    assert response.status_code == 200
    # check if in lite mode expected block hash is 0x1 and 0x2
    if expected_block_hash == EXPECTED_ABORT_HASHES:
        assert response.json()["aborted"] == EXPECTED_ABORT_HASHES
    contract_deploy_block_after_abort = get_block(block_number=1, parse=True)
    assert contract_deploy_block_after_abort["status"] == "ABORTED"
    assert_transaction(contract_deploy_info["tx_hash"], "REJECTED")
    invoke_block_after_abort = get_block(block_number=2, parse=True)
    assert invoke_block_after_abort["status"] == "ABORTED"
    assert_transaction(invoke_tx_hash, "REJECTED")

    # Newly deployed contract after abort should be accepted on L2
    contract_deploy_info = deploy(CONTRACT_PATH, inputs=["0"])
    contract_deploy_block = get_block(parse=True)
    assert contract_deploy_block["status"] == "ACCEPTED_ON_L2"
    assert_tx_status(contract_deploy_info["tx_hash"], "ACCEPTED_ON_L2")
