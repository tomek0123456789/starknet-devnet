"""UDC and its constants"""

from starkware.python.utils import to_bytes
from starkware.solidity.utils import load_nearby_contract
from starkware.starknet.services.api.contract_class import ContractClass

from starknet_devnet.predeployed_contract_wrapper import PredeployedContractWrapper


class UDC(PredeployedContractWrapper):
    """Universal deployer contract wrapper class"""

    CONTRACT_CLASS: ContractClass = None  # loaded lazily

    # Precalculated
    # HASH = to_bytes(compute_class_hash(contract_class=UDC.get_contract_class()))
    HASH = 3484004124736344420122298338254154090450773688458934993781007232228755339881
    HASH_BYTES = to_bytes(HASH)

    # Precalculated to fixed address
    # ADDRESS = calculate_contract_address_from_hash(salt=0, class_hash=HASH,
    # constructor_calldata=[], deployer_address=0)
    ADDRESS = 0x41A78E741E5AF2FEC34B695679BC6891742439F7AFB8484ECD7766661AD02BF

    def __init__(self, starknet_wrapper):
        self.starknet_wrapper = starknet_wrapper
        self.address = self.ADDRESS
        self.class_hash_bytes = self.HASH_BYTES

    @classmethod
    def get_contract_class(cls):
        """Returns contract class via lazy loading."""
        if not cls.CONTRACT_CLASS:
            cls.CONTRACT_CLASS = ContractClass.load(
                load_nearby_contract("UDC_OZ_0.5.0")
            )
        return cls.CONTRACT_CLASS

    @property
    def contract_class(self) -> ContractClass:
        """Same as `get_contract_class`, used by `PredeployedContractWrapper` parent"""
        return self.get_contract_class()

    async def _mimic_constructor(self):
        pass
