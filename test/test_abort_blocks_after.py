"""
Tests the abort block of the devnet.
"""

import pytest
import requests

from .settings import APP_URL
from .shared import ARTIFACTS_PATH
from .util import deploy, get_block
from .account import invoke
from .shared import (
    CONTRACT_PATH,
    GENESIS_BLOCK_NUMBER,
    PREDEPLOY_ACCOUNT_CLI_ARGS,
    PREDEPLOYED_ACCOUNT_ADDRESS,
    PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
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
def test_abort_blocks_after(expected_block_hash):
    """Test abort blocks after"""

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
    # transaction should be

    print("contract_deploy_block[""]")
    print(contract_deploy_block["block_hash"])
    
    response = abort_blocks_after(contract_deploy_block["block_hash"])
    print("abort_blocks_after")
    print(response)
    print(response.json())
    assert response.status_code == 200
    assert contract_deploy_block["status"] == "ABORTED"
    assert_tx_status(contract_deploy_info["tx_hash"], "REJECTED")

    # Use this later
    # TODO: add second tests with many blocks and many transactions 
    # increase and assert balance
    # invoke_tx_hash = invoke(
    #     calls=[(deploy_info["address"], "increase_balance", [1, 1])],
    #     account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
    #     private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    # )
