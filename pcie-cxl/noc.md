# What's outcome of Network of chip 
![SPR](image.png)
The Cache Home Agent consists of Address Generation Unit(AGU), Address Translation Unit(ATU). The AGU is responsible for generating the physical address from the virtual address. The ATU is responsible for translating the physical address to the cache line address. The scheduling mechanism in the CPU includes:

1. the fastest route from one CHA to the other.
2. the scheduler for fetch exclusive/ fetch share/ invalidate before sharing or upgrade to directory based coherence protocol.
3. CXL related: how to save message for remote fabric accesses?
4. Is Intel HotChips' optics fabric good enough for in Rack communication?

## Software hint using CXL.io to tell remote caching policy
The software hint is a hint to the remote caching policy. SDM's hint is a 4-bit vendor specific field in the CXL.io request to the mailbox to let the shared cacheline stuck there to save RTTs. But it's obviously an abuse to the mailbox since managing the cacheline level with control flow throttling the CXL bandwidth is not feasible. I think ZeroPoints' demo that utilzing mailbox for the compression memory is better use of mailbox. Programmably hinting the remote caching policy is a good idea. But I think it's a sophisticated timing problem requires observability tool for memory requests.

## Problem of using Distributed Shared Memory
Another Distributed System over the current infra.

## Reference
1. SDM: Sharing-Enabled Disaggregated Memory System with Cache Coherent Compute Express Link
2. Demystifying CXL with Genuine Devices
3. [Intel Optics Graph Processor PoC](https://www.theregister.com/2023/09/01/intel_graph_analytics_chip/)
4. 