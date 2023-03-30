"""
Tests the abort block functionality.
"""
from test.rpc.rpc_utils import rpc_call

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

NOT_EXISTING_BLOCK = "0x9"


def abort_blocks_after(block_hash):
    """Abort blocks after certain block hash"""
    return requests.post(
        f"{APP_URL}/abort_blocks_after", json={"blockHash": block_hash}
    )


@devnet_in_background()
def test_abort_not_existing_block():
    """Test abort of not existing block."""
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

    # Test RPC get block status
    rpc_response = rpc_call("starknet_getBlockWithTxs", params={"block_id": "latest"})
    assert rpc_response["result"]["status"] == "REJECTED"


@devnet_in_background(*PREDEPLOY_ACCOUNT_CLI_ARGS)
def test_abort_many_blocks_many_transactions():
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
    assert response.json()["aborted"] == [contract_deploy_block["block_hash"], invoke_block["block_hash"]]
    contract_deploy_block_after_abort = get_block(block_number=1, parse=True)
    assert contract_deploy_block_after_abort["status"] == "ABORTED"
    assert_transaction(contract_deploy_info["tx_hash"], "REJECTED")
    invoke_block_after_abort = get_block(block_number=2, parse=True)
    assert invoke_block_after_abort["status"] == "ABORTED"
    assert_transaction(invoke_tx_hash, "REJECTED")

    # Test RPC get block status
    rpc_response = rpc_call("starknet_getBlockWithTxs", params={"block_id": "latest"})
    assert rpc_response["result"]["status"] == "REJECTED"

    # Newly deployed contract after abort should be accepted on L2
    contract_deploy_info = deploy(CONTRACT_PATH, inputs=["0"])
    contract_deploy_block = get_block(parse=True)
    assert contract_deploy_block["status"] == "ACCEPTED_ON_L2"
    assert_tx_status(contract_deploy_info["tx_hash"], "ACCEPTED_ON_L2")
