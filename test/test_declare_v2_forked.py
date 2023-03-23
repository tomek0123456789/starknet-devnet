"""
Test declare v2 in forked mode.
The benefit of having this in a separate file is the ability to parallelize.
"""

from starkware.starknet.services.api.contract_class.contract_class import ContractClass
from starkware.starknet.services.api.contract_class.contract_class_utils import (
    load_sierra,
)

from .account import send_declare_v2
from .settings import APP_URL
from .shared import (
    CONTRACT_1_CASM_PATH,
    CONTRACT_1_PATH,
    EXPECTED_CLASS_1_HASH,
    PREDEPLOYED_ACCOUNT_ADDRESS,
    PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
)
from .test_declare_v2 import assert_declare_v2_accepted, load_cairo1_contract
from .testnet_deployment import (
    TESTNET_DEPLOYMENT_BLOCK,
    TESTNET_FORK_PARAMS,
    TESTNET_URL,
)
from .util import (
    assert_class_by_hash_not_present,
    assert_compiled_class_by_hash,
    assert_compiled_class_by_hash_not_present,
    assert_tx_status,
    devnet_in_background,
    get_class_by_hash,
)


@devnet_in_background(
    *TESTNET_FORK_PARAMS, "--fork-block", str(TESTNET_DEPLOYMENT_BLOCK - 1)
)
def test_declare_v2_and_get_class_by_hash():
    """Test class declaration and class getting by hash"""

    assert_class_by_hash_not_present(
        class_hash=EXPECTED_CLASS_1_HASH, feeder_gateway_url=TESTNET_URL
    )
    assert_class_by_hash_not_present(
        class_hash=EXPECTED_CLASS_1_HASH, feeder_gateway_url=APP_URL
    )
    assert_compiled_class_by_hash_not_present(
        class_hash=EXPECTED_CLASS_1_HASH, feeder_gateway_url=TESTNET_URL
    )
    assert_compiled_class_by_hash_not_present(
        class_hash=EXPECTED_CLASS_1_HASH, feeder_gateway_url=APP_URL
    )

    contract_class, _, compiled_class_hash = load_cairo1_contract()

    declaration_resp = send_declare_v2(
        contract_class=contract_class,
        compiled_class_hash=compiled_class_hash,
        sender_address=PREDEPLOYED_ACCOUNT_ADDRESS,
        sender_key=PREDEPLOYED_ACCOUNT_PRIVATE_KEY,
    )
    assert_declare_v2_accepted(declaration_resp)

    declare_info = declaration_resp.json()
    assert int(declare_info["class_hash"], 16) == int(EXPECTED_CLASS_1_HASH, 16)
    assert_tx_status(declare_info["transaction_hash"], "ACCEPTED_ON_L2")

    assert_class_by_hash_not_present(
        class_hash=EXPECTED_CLASS_1_HASH, feeder_gateway_url=TESTNET_URL
    )

    # assert class by hash, util.assert_class_by_hash not applicable
    resp = get_class_by_hash(EXPECTED_CLASS_1_HASH, feeder_gateway_url=APP_URL)
    assert resp.status_code == 200, resp.text
    sierra_dict = resp.json()
    sierra_dict.pop("sierra_program_debug_info", None)
    sierra = ContractClass.load(sierra_dict)
    assert load_sierra(CONTRACT_1_PATH) == sierra

    assert_compiled_class_by_hash_not_present(
        class_hash=EXPECTED_CLASS_1_HASH, feeder_gateway_url=TESTNET_URL
    )
    assert_compiled_class_by_hash(
        class_hash=EXPECTED_CLASS_1_HASH,
        expected_path=CONTRACT_1_CASM_PATH,
        feeder_gateway_url=APP_URL,
    )
