#!/bin/bash

set -eu

if [ -z "${CAIRO_1_COMPILER_MANIFEST-}" ]; then
    echo "Error: CAIRO_1_COMPILER_MANIFEST must be set"
    exit 1
fi

ARTIFACTS_DIRECTORY="test/artifacts/contracts/cairo1"

# recreate artifacts directory
rm -rf "$ARTIFACTS_DIRECTORY"
mkdir -p "$ARTIFACTS_DIRECTORY"

compiler_version=$(cargo run \
    --manifest-path "$CAIRO_1_COMPILER_MANIFEST" \
    --bin starknet-sierra-compile \
    -- --version \
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

    # compile to sierra
    cargo run --bin starknet-compile --manifest-path "$CAIRO_1_COMPILER_MANIFEST" -- "$contract" "$sierra_output"

    # compile to casm
    cargo run --bin starknet-sierra-compile --manifest-path "$CAIRO_1_COMPILER_MANIFEST" -- "$sierra_output" "$casm_output"

    number_of_contracts=$((number_of_contracts+1))
done

echo "Compiled $number_of_contracts Cairo files successfully"