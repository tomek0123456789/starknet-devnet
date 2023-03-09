"""Compilation utilities"""

import json
import os
import subprocess
import tempfile

from starkware.starknet.definitions.error_codes import StarknetErrorCode
from starkware.starknet.services.api.contract_class.contract_class import (
    CompiledClass,
    ContractClass,
)

from starknet_devnet.contract_class_utils import load_casm
from starknet_devnet.util import StarknetDevnetException


def compile_cairo(
    contract_class: ContractClass, compiler_manifest: str
) -> CompiledClass:
    """Compile ContractClass to CompiledClass using compiler_manifest"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        contract_json = os.path.join(tmp_dir, "contract.json")
        contract_casm = os.path.join(tmp_dir, "contract.casm")

        with open(contract_json, mode="w", encoding="utf-8") as tmp_file:
            contract_class_dumped = contract_class.dump()
            contract_class_dumped["abi"] = json.loads(contract_class_dumped["abi"])
            json.dump(contract_class_dumped, tmp_file)

        compilation_args = [
            "cargo",
            "run",
            "--bin",
            "starknet-sierra-compile",
            "--manifest-path",
            compiler_manifest,
            contract_json,
            contract_casm,
        ]
        compilation = subprocess.run(compilation_args, capture_output=True, check=False)
        if compilation.returncode:
            stderr = compilation.stderr.decode("utf-8")
            raise StarknetDevnetException(
                code=StarknetErrorCode.UNEXPECTED_FAILURE,
                message=f"Failed compilation to casm! {stderr}",
            )

        compiled_class = load_casm(contract_casm)
        return compiled_class
