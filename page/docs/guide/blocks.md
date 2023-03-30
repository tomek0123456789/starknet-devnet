---
sidebar_position: 8
---

# Blocks

Devnet starts with a genesis block (with block number equal to `0` and block hash equal to `"0x0"`).

A new block is generated with each new transaction unless you opt for [creating blocks on demand](#create-a-block-on-demand).

### Create an empty block

To create an empty block without transactions, `POST` a request to `/create_block`:

```
POST /create_block
```

Response:

```
{'block_hash': '0x115e1b390cafa7942b6ab141ab85040defe7dee9bef3bc31d8b5b3d01cc9c67'}
```

### Create a block on demand

If you start Devnet with `--blocks-on-demand` CLI option, all transactions will be pending and stored in a pending block (targetable via block ID `"pending"`).
To create a block on demand, send a `POST` request to `/create_block`. This will convert the pending block to the latest block (targetable via block ID `"latest"`), giving it a block hash and a block number. All subsequent transactions will be stored to a new pending block.

In case of demanding block creation with no pending transactions, a new empty block will be generated.

The creation of the genesis block is not affected by this feature.

```
POST /create_block
```

Response:

```
{'block_hash': '0x115e1b390cafa7942b6ab141ab85040defe7dee9bef3bc31d8b5b3d01cc9c67'}
```
