# Fabric Manager

The fabric manager is the place where coherence, placement, telemetry, and policy start touching each other.

The question I care about is: how do we co-design PMU/PEBS-like traces so they become programmable enough for policy, but still cheap enough to trust?

## The partial traces collected

The trace should answer:

- which agent issued the request;
- which address or region was touched;
- whether the request was local, remote, or forwarded;
- whether the line moved ownership;
- whether the latency came from queueing, fabric traversal, or coherence.

That is already more structure than a normal counter. It is closer to a compressed transaction log.

## Software management for the coherency

Software should not manage cache coherence at cache-line frequency. That path is too fast and too timing-sensitive. Software can manage policy around coherence:

- region ownership;
- migration thresholds;
- replication policy;
- admission into remote caches;
- throttling when a fabric path becomes noisy.

The hardware should expose enough state to let software act at region or epoch granularity.

1. [NeoMem](https://github.com/PKUZHOU/NeoMem-MICRO-2024)
