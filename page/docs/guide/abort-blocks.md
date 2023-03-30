---
sidebar_position: 19
---
# Abort blocks

This functionality allows to simulate blocks abort that can occur on mainnet.


## Abort Blocks After

Abort blocks and reject transactions from given block hash to last block. 

```
POST /abort_blocks
{
    "startingBlockHash": BLOCK_HASH
}
```

Response:
```
{
    "aborted": [BLOCK_HASH_0, BLOCK_HASH_1, ...]
}
```
