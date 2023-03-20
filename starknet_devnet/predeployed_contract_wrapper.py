"""Parent for predeployed contract wrapper classes"""
from abc import ABC

from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet


class PredeployedContractWrapper(ABC):
    """Parent class for all predeployed contract wrapper classes"""

    # Cannot import it because of circular imports
    # from .starknet_wrapper import StarknetWrapper

    starknet_wrapper: "StarknetWrapper"
    address: int
    class_hash_bytes: bytes
    contract_class: ContractClass

    # Value will be set by deploy
    contract: StarknetContract

    async def _mimic_constructor(self):
        raise NotImplementedError()

    async def deploy(self):
        """Deploy the contract wrapper to devnet"""
        starknet: Starknet = self.starknet_wrapper.starknet

        await starknet.state.state.set_contract_class(
            self.class_hash_bytes, self.contract_class
        )

        # pylint: disable=protected-access
        starknet: Starknet = self.starknet_wrapper.starknet
        starknet.state.state.cache._class_hash_writes[
            self.address
        ] = self.class_hash_bytes
        # replace with await starknet.state.state.deploy_contract
        # await starknet.state.state.deploy_contract(self.address, self.class_hash_bytes)
        # For now, it fails for fee token since the address is the same as the
        # ETH Token, see:
        # https://starkscan.co/token/0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7:
        # Requested contract address
        # 0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7
        # is unavailable for deployment

        await self._mimic_constructor()

        self.contract = StarknetContract(
            state=starknet.state,
            abi=self.contract_class.abi,
            contract_address=self.address,
            deploy_call_info=None,
        )
