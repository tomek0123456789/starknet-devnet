---
sidebar_position: 11
---
# Advancing time

Block timestamp can be manipulated by setting the exact time or setting the time offset. Timestamps methods won't generate a new block, but they will modify the time of the following blocks. All values should be set in [**Unix time**](https://en.wikipedia.org/wiki/Unix_time) and seconds.

## Set time

Sets the exact time and generates a new block (only possible if there are no pending transactions). All subsequent blocks will keep the set offset.

```
POST /set_time
{
    "time": TIME_IN_SECONDS
}
```

Warning: block time can be set in the past and lead to unexpected behaviour!

## Increase time

Increases the block timestamp by the provided amount and generates a new block (only possible if there are no pending transactions). All subsequent blocks will keep this increment.

```
POST /increase_time
{
    "time": TIME_IN_SECONDS
}
```

## Start time arg

Devnet can be started with the `--start-time` argument.

```
starknet-devnet --start-time START_TIME_IN_SECONDS
```

## Timeout

Timeout can be passed to Devnet's HTTP server. This makes it easier to deploy and manage large contracts that take longer to execute and may otherwise result in an error `ServerDisconnectedError`.

```
starknet-devnet --timeout TIMEOUT
```
