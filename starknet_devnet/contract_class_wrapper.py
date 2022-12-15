"""Starknet ContractClass wrapper utilities"""

import os
from dataclasses import dataclass

from starkware.python.utils import to_bytes
from starkware.starknet.services.api.contract_class import ContractClass


@dataclass
class ContractClassWrapper:
    """Wrapper of ContractClass"""

    contract_class: ContractClass
    hash_bytes: bytes


DEFAULT_ACCOUNT_PATH = os.path.abspath(
    os.path.join(
        __file__,
        os.pardir,
        "accounts_artifacts",
        "OpenZeppelin",
        "0.5.1",
        "Account.cairo",
        "Account.json",
    )
)
DEFAULT_ACCOUNT_CLASS_HASH = 0x4D07E40E93398ED3C76981E72DD1FD22557A78CE36C0515F679E27F0BB5BC5F
DEFAULT_ACCOUNT_HASH_BYTES = to_bytes(DEFAULT_ACCOUNT_CLASS_HASH)
