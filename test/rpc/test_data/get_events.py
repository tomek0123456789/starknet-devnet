"""
RPC get events test data.
"""
import re
from typing import Optional, Union, List

from test.shared import (
    EXPECTED_FEE_TOKEN_ADDRESS,
    FEE_CHARGED_EVENT_KEY,
    INCREASE_BALANCE_CALLED_EVENT_KEY,
    PREDEPLOY_ACCOUNT_CLI_ARGS,
    PREDEPLOYED_ACCOUNT_ADDRESS,
)

from starknet_devnet.blueprints.rpc.utils import rpc_felt


def create_get_events_filter(
        *,
        from_block: Union[int, str] = 0,
        to_block: Union[int, str] = "latest",
        address: Optional[str] = rpc_felt(EXPECTED_FEE_TOKEN_ADDRESS),
        keys: Optional[List[str]] = None,
        chunk_size: int = 10,
        continuation_token: Optional[str] = None
) -> dict:
    """
    Method that creates ``filter`` parameter for `get_events` RPC call.

    :param from_block: Identifier of the block (number of hash) from which the events start.
        The value can be a rpc felt, an int or literals "latest" or "pending". Defaults to 0.
    :param to_block: Identifier of the block (number or hash) to which the events end.
        The value can be a rpc felt, an int or literals "latest" or "pending". Defaults to "latest".
    :param address: Address of the contract.
    :param keys: Names of events that are searched for in rpc felt form.
    :param chunk_size: Size of returned one chunk of events, defaults to 10.
    :param continuation_token: (optional) String with a continuation token.
    
    :return: `filter` param.
    """
    if keys is None:
        keys = [rpc_felt(FEE_CHARGED_EVENT_KEY)]
    filter_body = {
        "from_block": parse_block_delimiter_parameter(from_block),
        "keys": keys,
        "to_block": parse_block_delimiter_parameter(to_block),
        "chunk_size": chunk_size,
    }
    if address is not None:
        filter_body["address"] = address
    if continuation_token is not None:
        filter_body["continuation_token"] = continuation_token
    return {"filter": filter_body}


def parse_block_delimiter_parameter(block_delimiter) -> dict:
    if block_delimiter in ("latest", "pending"):
        return block_delimiter
    if isinstance(block_delimiter, int):
        return {"block_number": block_delimiter}
    return {"block_hash": block_delimiter}


EVENT_FEE_ADDRESS = rpc_felt(
    0xBEBE7DEC64B911AEFFECC184AFCEFA6470E3B3652A1605E42D643E1EA9093D
)
FEE_CHARGING_IN_BLOCK_2_EVENT = [
    rpc_felt(int(PREDEPLOYED_ACCOUNT_ADDRESS, 16)),
    EVENT_FEE_ADDRESS,
    rpc_felt(0x73B00ED0C000),  # WEI
    rpc_felt(0),
]
FEE_CHARGING_IN_BLOCK_3_EVENT = [
    rpc_felt(int(PREDEPLOYED_ACCOUNT_ADDRESS, 16)),
    EVENT_FEE_ADDRESS,
    rpc_felt(0x015254FFDB4000),  # WEI
    rpc_felt(0),
]


GET_EVENTS_TEST_DATA = [
    (
        [*PREDEPLOY_ACCOUNT_CLI_ARGS],
        create_get_events_filter(keys=[rpc_felt(FEE_CHARGED_EVENT_KEY), rpc_felt(INCREASE_BALANCE_CALLED_EVENT_KEY)]),
        [
            FEE_CHARGING_IN_BLOCK_2_EVENT,
            FEE_CHARGING_IN_BLOCK_3_EVENT,
        ],
    ),
    (
        [*PREDEPLOY_ACCOUNT_CLI_ARGS],
        create_get_events_filter(from_block=rpc_felt("0x0")),
        [
            FEE_CHARGING_IN_BLOCK_2_EVENT,
            FEE_CHARGING_IN_BLOCK_3_EVENT,
        ],
    ),
    (
        [*PREDEPLOY_ACCOUNT_CLI_ARGS],
        create_get_events_filter(from_block=rpc_felt("0x0"), to_block=2),
        [FEE_CHARGING_IN_BLOCK_2_EVENT],
    ),
    (
        [*PREDEPLOY_ACCOUNT_CLI_ARGS],
        create_get_events_filter(from_block=3, to_block=3),
        [FEE_CHARGING_IN_BLOCK_3_EVENT],
    ),
    (
        [*PREDEPLOY_ACCOUNT_CLI_ARGS],
        create_get_events_filter(from_block=2, to_block=3),
        [
            FEE_CHARGING_IN_BLOCK_2_EVENT,
            FEE_CHARGING_IN_BLOCK_3_EVENT,
        ],
    ),
]
