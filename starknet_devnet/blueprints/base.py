"""
Base routes
"""
from flask import Blueprint, Response, jsonify, request
from starkware.starkware_utils.error_handling import StarkErrorCode

from starknet_devnet.fee_token import FeeToken
from starknet_devnet.state import state
from starknet_devnet.util import (
    StarknetDevnetException,
    check_valid_dump_path,
    parse_hex_string,
)

base = Blueprint("base", __name__)


def extract_int(value):
    """extract int from float if an integer value"""
    return isinstance(value, float) and value.is_integer() and int(value) or value


def extract_positive(request_json, prop_name: str):
    """Expects `prop_name` from `request_json` and expects it to be positive"""
    value = extract_int(request_json.get(prop_name))

    if value is None:
        raise StarknetDevnetException(
            code=StarkErrorCode.MALFORMED_REQUEST,
            message=f"{prop_name} value must be provided.",
            status_code=400,
        )

    if not isinstance(value, int) or isinstance(value, bool):
        raise StarknetDevnetException(
            code=StarkErrorCode.MALFORMED_REQUEST,
            message=f"{prop_name} value must be an integer.",
            status_code=400,
        )

    if value < 0:
        raise StarknetDevnetException(
            code=StarkErrorCode.MALFORMED_REQUEST,
            message=f"{prop_name} value must be greater than 0.",
            status_code=400,
        )

    return value


def hex_converter(request_json, prop_name: str, convert=parse_hex_string) -> int:
    """Parse value from hex string to int, or values from hex strings to ints"""
    value = request_json.get(prop_name)
    if value is None:
        raise StarknetDevnetException(
            code=StarkErrorCode.MALFORMED_REQUEST,
            status_code=400,
            message=f"{prop_name} value or values must be provided.",
        )

    try:
        return convert(value)
    except (ValueError, TypeError) as error:
        message = f"{prop_name} value or values must be a hex string."
        raise StarknetDevnetException(
            code=StarkErrorCode.MALFORMED_REQUEST,
            status_code=400,
            message=message,
        ) from error


@base.route("/is_alive", methods=["GET"])
def is_alive():
    """Health check endpoint."""
    return "Alive!!!"


@base.route("/restart", methods=["POST"])
async def restart():
    """Restart the starknet_wrapper"""
    await state.reset()
    return Response(status=200)


@base.route("/dump", methods=["POST"])
def dump():
    """Dumps the starknet_wrapper"""

    request_dict = request.json or {}
    dump_path = request_dict.get("path") or state.dumper.dump_path
    if not dump_path:
        raise StarknetDevnetException(
            code=StarkErrorCode.MALFORMED_REQUEST,
            message="No path provided.",
            status_code=400,
        )

    try:
        check_valid_dump_path(dump_path)
    except ValueError as error:
        raise StarknetDevnetException(
            code=StarkErrorCode.MALFORMED_REQUEST,
            message=str(error),
            status_code=400,
        ) from error

    state.dumper.dump(dump_path)
    return Response(status=200)


@base.route("/load", methods=["POST"])
def load():
    """Loads the starknet_wrapper"""

    request_dict = request.json or {}
    load_path = request_dict.get("path")
    if not load_path:
        raise StarknetDevnetException(
            code=StarkErrorCode.MALFORMED_REQUEST,
            message="No path provided.",
            status_code=400,
        )

    state.load(load_path)
    return Response(status=200)


@base.route("/increase_time", methods=["POST"])
async def increase_time():
    """Increases the block timestamp offset and generates a new block"""
    request_dict = request.json or {}
    time_s = extract_positive(request_dict, "time")

    # Increase block time only when there are no pending transactions
    if not state.starknet_wrapper.pending_txs:
        state.starknet_wrapper.increase_block_time(time_s)
        block = await state.starknet_wrapper.generate_latest_block()
        return jsonify(
            {"timestamp_increased_by": time_s, "block_hash": hex(block.block_hash)}
        )

    raise StarknetDevnetException(
        code=StarkErrorCode.INVALID_REQUEST,
        status_code=400,
        message="Block time can be increased only if there are no pending transactions.",
    )


@base.route("/set_time", methods=["POST"])
async def set_time():
    """Sets the block timestamp offset and generates a new block"""
    request_dict = request.json or {}
    time_s = extract_positive(request_dict, "time")

    # Set block time only when there are no pending transactions
    if not state.starknet_wrapper.pending_txs:
        state.starknet_wrapper.set_block_time(time_s)
        block = await state.starknet_wrapper.generate_latest_block()
        return jsonify({"block_timestamp": time_s, "block_hash": hex(block.block_hash)})

    raise StarknetDevnetException(
        code=StarkErrorCode.MALFORMED_REQUEST,
        status_code=400,
        message="Block time can be set only if there are no pending transactions.",
    )


@base.route("/account_balance", methods=["GET"])
async def get_balance():
    """Gets balance for the address"""
    address = request.args.get("address", type=lambda x: int(x, 16))

    balance = await state.starknet_wrapper.fee_token.get_balance(address)
    return jsonify({"amount": balance, "unit": "wei"})


@base.route("/predeployed_accounts", methods=["GET"])
def get_predeployed_accounts():
    """Get predeployed accounts"""
    accounts = state.starknet_wrapper.accounts
    return jsonify([account.to_json() for account in accounts])


@base.route("/fee_token", methods=["GET"])
async def get_fee_token():
    """Get the address of the fee token"""
    fee_token_address = FeeToken.ADDRESS
    symbol = FeeToken.SYMBOL
    return jsonify({"symbol": symbol, "address": hex(fee_token_address)})


@base.route("/mint", methods=["POST"])
async def mint():
    """Mint token and transfer to the provided address"""
    request_json = request.json or {}

    address = hex_converter(request_json, "address")
    amount = extract_positive(request_json, "amount")
    is_lite = request_json.get("lite", False)

    tx_hash = await state.starknet_wrapper.fee_token.mint(
        to_address=address, amount=amount, lite=is_lite
    )

    new_balance = await state.starknet_wrapper.fee_token.get_balance(address)
    return jsonify({"new_balance": new_balance, "unit": "wei", "tx_hash": tx_hash})


@base.route("/create_block", methods=["POST"])
async def create_block():
    """Create block with pending transactions."""
    block = await state.starknet_wrapper.generate_latest_block()

    return jsonify({"block_hash": hex(block.block_hash)})


@base.route("/fork_status", methods=["GET"])
async def fork_status():
    """Get fork status"""
    config = state.starknet_wrapper.config
    if config.fork_network:
        return jsonify({"url": config.fork_network.url, "block": config.fork_block})
    return jsonify({})


@base.route("/abort_blocks_after", methods=["POST"])
async def abort_blocks_after():
    """Abort blocks and transactions from given block hash to last block."""
    request_json = request.json or {}
    current_block = await state.starknet_wrapper.blocks.get_by_hash(
        hex(hex_converter(request_json, "blockHash"))
    )
    last_block = await state.starknet_wrapper.blocks.get_last_block()
    block_hashes = []

    # Abort blocks
    for block_number in range(current_block.block_number, last_block.block_number + 1):
        block = await state.starknet_wrapper.blocks.get_by_number(block_number)
        await state.starknet_wrapper.blocks.abort_block_by_hash(hex(block.block_hash))

        # Reject transactions
        for transaction in block.transactions:
            await state.starknet_wrapper.transactions.reject_transaction(
                tx_hash=transaction.transaction_hash
            )

        block_hashes.append(hex(block.block_hash))

    return jsonify({"aborted": block_hashes})
