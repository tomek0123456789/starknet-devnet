"""Test class replacement"""

from .account import declare, deploy, invoke
from .shared import (
    PREDEPLOY_ACCOUNT_CLI_ARGS,
    PREDEPLOYED_ACCOUNT_ADDRESS,
    PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    REPLACEABLE_ABI_PATH,
    REPLACEABLE_CONTRACT_PATH,
    REPLACING_ABI_PATH,
    REPLACING_CONTRACT_PATH,
)
from .test_state_update import get_state_update
from .util import (
    assert_class_hash_at_address,
    assert_hex_equal,
    assert_tx_status,
    call,
    devnet_in_background,
)


@devnet_in_background(*PREDEPLOY_ACCOUNT_CLI_ARGS)
def test_replace_class_happy_path():
    """Deploy a contract, replace its class, assert it's replaced"""

    # declare original
    replaceable_declare_info = declare(
        REPLACEABLE_CONTRACT_PATH,
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
        max_fee=int(1e18),
    )

    # declare the replacing class
    replacing_declare_info = declare(
        REPLACING_CONTRACT_PATH,
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
        max_fee=int(1e18),
    )
    new_class_hash = replacing_declare_info["class_hash"]

    replaceable_deploy_info = deploy(
        class_hash=replaceable_declare_info["class_hash"],
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
        max_fee=int(1e18),
    )
    contract_address = replaceable_deploy_info["address"]

    foo_before_replacement = call(
        function="foo",
        address=contract_address,
        abi_path=REPLACEABLE_ABI_PATH,
    )
    assert int(foo_before_replacement) == 42

    replacement_tx_hash = invoke(
        calls=[(contract_address, "replace", [int(new_class_hash, 16)])],
        account_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        private_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
        max_fee=int(1e18),
    )
    assert_tx_status(replacement_tx_hash, "ACCEPTED_ON_L2")

    foo_after_replacement = call(
        function="foo",
        address=contract_address,
        # REPLACEABLE_ABI_PATH could be used with the same effect
        abi_path=REPLACING_ABI_PATH,
    )
    assert foo_before_replacement != foo_after_replacement
    assert int(foo_after_replacement) == 43

    # assert state update contains replacement info
    state_update = get_state_update()
    replaced_classes = state_update["state_diff"]["replaced_classes"]
    assert len(replaced_classes) == 1
    assert_hex_equal(replaced_classes[0]["address"], contract_address)
    assert_hex_equal(replaced_classes[0]["class_hash"], new_class_hash)

    # assert retrieved class is the new one
    assert_class_hash_at_address(contract_address, new_class_hash)
