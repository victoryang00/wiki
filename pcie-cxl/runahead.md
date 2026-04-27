# Runahead

Runahead is a technique for paying memory latency before the program reaches the blocking point. The CPU enters a speculative mode after a long-latency miss, continues executing future instructions, and uses those future instructions to discover more misses.

The key trick is that runahead is not trying to retire useful work. It is trying to reveal future addresses.

```text
normal execution hits a long miss
        |
        v
enter runahead mode
        |
        v
execute with invalid values, but keep address generation alive
        |
        v
prefetch future misses
```

## Why it matters for CXL

CXL memory makes the miss penalty large enough that "just add MSHRs" is not satisfying. If the code has predictable future misses, runahead can turn serialized pain into earlier pain.

The CXL version of the question is:

- can we run ahead across remote-memory dependent code?
- can invalid values still produce useful future addresses?
- can the compiler mark which computations are address-relevant?

## Vector runahead

Vector machines expose a stronger version of the same idea. If the vector load pattern is visible before the load retires, the machine can prefetch the next lanes or next tiles. For memory-bound vector loops, the useful work is often address discovery plus bandwidth shaping.

## Reference
1. [Runahead Execution: An Alternative to Very Large Instruction Windows for Out-of-Order Processors](https://ieeexplore.ieee.org/document/1183532)
2. [Vector Runahead](https://users.elis.ugent.be/~leeckhou/papers/isca2021.pdf) // This group went to Intel mostly
3. [Continuous Runahead: Transparent Hardware Acceleration for Memory Intensive Workload](https://ieeexplore.ieee.org/document/7783764)
