"""
Tests the abort block functionality.
"""

import pytest
import requests

from .settings import APP_URL
from .shared import ARTIFACTS_PATH
from .util import deploy, get_block
from .account import invoke
from .shared import (
    CONTRACT_PATH,
    PREDEPLOY_ACCOUNT_CLI_ARGS,
)
from .util import (
    assert_transaction,
    assert_tx_status,
    deploy,
    get_block,
)

EXPECTED_SALTY_DEPLOY_BLOCK_HASH_LITE_MODE = "0x1"

def abort_blocks_after(block_hash):
    """TODO: """
    return requests.post(
        f"{APP_URL}/abort_blocks_after", json={"blockHash": block_hash}
    )

@pytest.mark.usefixtures("run_devnet_in_background")
@pytest.mark.parametrize(
    "run_devnet_in_background, expected_block_hash",
    [
        (
            [*PREDEPLOY_ACCOUNT_CLI_ARGS],
            "test",
        ),
    ],
    indirect=True,
)
def test_abort_single_block_single_transaction(expected_block_hash):
    """Test abort of single block and single transaction."""

    # Genesis block should be accepted on L2
    genesis_block = get_block(parse=True)
    assert genesis_block["status"] == "ACCEPTED_ON_L2"

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
    print("abort_blocks_after")
    print(response)
    print(response.json())
    print("contract_deploy_block_after_abort")
    print(contract_deploy_block_after_abort["transactions"][0])
    assert response.status_code == 200
    assert contract_deploy_block_after_abort["status"] == "ABORTED"
    assert_transaction(contract_deploy_info["tx_hash"], "REJECTED")
