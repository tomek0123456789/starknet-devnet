"""UDC and its constants"""

from starkware.solidity.utils import load_nearby_contract
from starkware.starknet.services.api.contract_class.contract_class import (
    CompiledClassBase,
    DeprecatedCompiledClass,
)
from starkware.starknet.testing.starknet import Starknet


class UDC:
    """Universal deployer contract wrapper class"""

    CONTRACT_CLASS: CompiledClassBase = None  # loaded lazily

    # Precalculated
    # HASH = compute_deprecated_class_hash(contract_class=UDC.get_contract_class())
    HASH = 0x7B3E05F48F0C69E4A65CE5E076A66271A527AFF2C34CE1083EC6E1526997A69

    # Precalculated to fixed address
    # ADDRESS = calculate_contract_address_from_hash(salt=0, class_hash=HASH,
    # constructor_calldata=[], deployer_address=0)
    ADDRESS = 0x41A78E741E5AF2FEC34B695679BC6891742439F7AFB8484ECD7766661AD02BF

    def __init__(self, starknet_wrapper):
        self.starknet_wrapper = starknet_wrapper

    @classmethod
    def get_contract_class(cls):
        """Returns contract class via lazy loading."""
        if not cls.CONTRACT_CLASS:
            cls.CONTRACT_CLASS = DeprecatedCompiledClass.load(
                load_nearby_contract("UDC_OZ_0.5.0")
            )
        return cls.CONTRACT_CLASS

    async def deploy(self):
        """Deploy token contract for charging fees."""
        starknet: Starknet = self.starknet_wrapper.starknet
        contract_class = UDC.get_contract_class()

        starknet.state.state.contract_classes[UDC.HASH] = contract_class

        # pylint: disable=protected-access
        starknet.state.state.cache._class_hash_writes[UDC.ADDRESS] = UDC.HASH
        # replace with await starknet.state.state.deploy_contract
        # TODO apply comment above
