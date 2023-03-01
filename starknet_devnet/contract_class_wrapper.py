"""Starknet CompiledClassBase wrapper utilities"""

import os
from dataclasses import dataclass

from starkware.starknet.services.api.contract_class.contract_class import (
    CompiledClassBase,
)


@dataclass
class CompiledClassWrapper:
    """Wrapper of CompiledClassBase"""

    contract_class: CompiledClassBase
    hash: int


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

DEFAULT_ACCOUNT_HASH = 0x4D07E40E93398ED3C76981E72DD1FD22557A78CE36C0515F679E27F0BB5BC5F
