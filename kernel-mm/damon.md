# DAMON

DAMON is interesting because it admits a hard truth: memory management decisions need access information, but exact access information is too expensive to collect on the hot path.

So the design is deliberately approximate. Instead of tracing every load/store, DAMON watches regions, adapts region granularity, and produces a heat map good enough for policy.

## Why it matters

For CXL and tiered memory, the naive policy is "hot pages local, cold pages remote." That sounds clean until the workload phase changes. Then the policy becomes a stale-history machine.

DAMON gives us a better starting point:

- observe access frequency without rewriting applications;
- detect phase behavior at region granularity;
- feed migration, reclaim, prefetch, and demotion policies;
- keep monitoring overhead bounded.

The catch is that DAMON is not a prophecy engine. It tells us what happened recently. A good placement system still needs to reason about the cost of being wrong.

## My mental model

```text
workload -> sampled access pattern -> region heat -> policy action
                                               |
                                               v
                                      migration cost model
```

The last box matters. A hot region should not move just because it crossed a threshold. It should move because the expected saved latency is larger than the migration cost plus disruption.

## Open questions

- How do we combine DAMON history with application hints?
- Can CXL devices expose enough counters to make the region model less host-centric?
- What is the right feedback loop when migration itself changes the observed access pattern?

## References

1. Linux DAMON documentation: `Documentation/admin-guide/mm/damon/`
2. DAMON-based reclaim and tiering discussions on LWN and linux-mm.
