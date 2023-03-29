"""
RPC classes endpoints
"""

from starkware.starknet.services.api.contract_class.contract_class import (
    DeprecatedCompiledClass,
)
from starkware.starkware_utils.error_handling import StarkException

from starknet_devnet.blueprints.rpc.schema import validate_schema
from starknet_devnet.blueprints.rpc.structures.payloads import rpc_contract_class
from starknet_devnet.blueprints.rpc.structures.types import (
    Address,
    BlockId,
    Felt,
    RpcError,
)
from starknet_devnet.blueprints.rpc.utils import assert_block_id_is_valid, rpc_felt
from starknet_devnet.state import state
from starknet_devnet.util import StarknetDevnetException


@validate_schema("getClass")
async def get_class(block_id: BlockId, class_hash: Felt) -> dict:
    """
    Get the contract class definition in the given block associated with the given hash
    """
    await assert_block_id_is_valid(block_id)  # T O D O   unused

    try:
        result_dict = await state.starknet_wrapper.get_class_by_hash(
            class_hash=int(class_hash, 16)
        )
    except StarknetDevnetException as ex:
        raise RpcError.from_spec_name("CLASS_HASH_NOT_FOUND") from ex

    # only works with cairo 0 classes
    loaded_class = DeprecatedCompiledClass.load(result_dict)
    return rpc_contract_class(loaded_class)


@validate_schema("getClassHashAt")
async def get_class_hash_at(block_id: BlockId, contract_address: Address) -> Felt:
    """
    Get the contract class hash in the given block for the contract deployed at the given address
    """
    await assert_block_id_is_valid(block_id)

    try:
        result = await state.starknet_wrapper.get_class_hash_at(
            int(contract_address, 16), block_id
        )
    except StarkException as ex:
        raise RpcError.from_spec_name("CLASS_HASH_NOT_FOUND") from ex

    return rpc_felt(result)


@validate_schema("getClassAt")
async def get_class_at(block_id: BlockId, contract_address: Address) -> dict:
    """
    Get the contract class definition in the given block at the given address
    """
    await assert_block_id_is_valid(block_id)

    try:
        result = await state.starknet_wrapper.get_class_by_address(
            int(contract_address, 16), block_id
        )
    except StarkException as ex:
        raise RpcError.from_spec_name("CONTRACT_NOT_FOUND") from ex

    return rpc_contract_class(result)
