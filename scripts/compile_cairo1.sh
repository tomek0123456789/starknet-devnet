#!/bin/bash

set -eu

CAIRO_1_COMPILER_MANIFEST=$(<.cairo-compiler-manifest-location)

ARTIFACTS_DIRECTORY="test/artifacts/contracts/cairo1"

# recreate artifacts directory
rm -rf "$ARTIFACTS_DIRECTORY"
mkdir -p "$ARTIFACTS_DIRECTORY"

compiler_version=$(
    cargo run \
        --manifest-path "$CAIRO_1_COMPILER_MANIFEST" \
        --bin starknet-sierra-compile \
        -- --version
)
echo "Compiling Cairo 1 contracts with $compiler_version"

number_of_contracts=0
for contract in "test/contracts/cairo1"/*.cairo; do
    basename=$(basename "$contract")

    # create contract artifact directory
    directory="$ARTIFACTS_DIRECTORY/${basename}"
    mkdir -p "$directory"

    without_extension="${basename%.*}"
    sierra_output="$directory/$without_extension.json"
    casm_output="$directory/$without_extension.casm"
    abi_output="$directory/${without_extension}_abi.json"

    # compile to sierra
    cargo run --bin starknet-compile \
        --manifest-path "$CAIRO_1_COMPILER_MANIFEST" \
        -- \
        --allowed-libfuncs-list-name experimental_v0.1.0 \
        "$contract" "$sierra_output"

    jq ".abi" "$sierra_output" >"$abi_output"

    # compile to casm
    cargo run --bin starknet-sierra-compile \
        --manifest-path "$CAIRO_1_COMPILER_MANIFEST" \
        -- \
        --allowed-libfuncs-list-name experimental_v0.1.0 \
        "$sierra_output" "$casm_output"

    number_of_contracts=$((number_of_contracts + 1))
done

echo "Compiled $number_of_contracts Cairo files successfully"
