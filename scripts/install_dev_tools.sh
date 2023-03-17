#!/bin/bash

set -e

echo "npm: $(npm --version)"
echo "npm: $(node --version)"
echo "pip: $(pip --version)"
echo "pip3: $(pip3 --version)"
echo "python: $(python --version)"
echo "python3: $(python3 --version)"

pip3 install -U poetry==1.3
echo "poetry: $(poetry --version)"

# https://www.rust-lang.org/tools/install
# need rust to install cairo-rs-py
if rustc --version; then
    echo "rustc installed"
else
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
fi

# setup cairo1 compiler
if [ -z "$CAIRO_1_COMPILER_MANIFEST" ]; then
    mkdir cairo-compiler
    git clone git@github.com:starkware-libs/cairo.git cairo-compiler
    CAIRO_1_COMPILER_MANIFEST="cairo-compiler/Cargo.toml"
else
    echo "Using Cairo compiler at $CAIRO_1_COMPILER_MANIFEST"
fi

cargo run --bin starknet-compile \
    --manifest-path "$CAIRO_1_COMPILER_MANIFEST" \
    -- \
    --version

# this enables testing
echo "$CAIRO_1_COMPILER_MANIFEST" >.cairo-compiler-manifest-location

# install dependencies
poetry install --no-ansi
poetry lock --check
npm ci
