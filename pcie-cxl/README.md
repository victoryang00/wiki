# PCIe and CXL

CXL is not just "PCIe with memory semantics." It changes the way software can lie to itself about locality.

My view: the interesting CXL problem is not only computational storage, near-data processing, or transparent tiering. It is the combination of all three with a brutal latency model. If the application still behaves as if every pointer is local and every cache miss is equal, CXL becomes a slower NUMA node with better marketing.

## What I care about

- CXL.mem as a placement and paging problem.
- CXL.cache as an ownership and coherence problem.
- CXL.io as a control path that should not be abused as a data-plane hammer.
- Device-side compute as a way to move work only when moving data is worse.

## The software shape I want

Applications should expose enough intent to keep shared state small and structured. If two hosts share a massive memory pool but constantly exchange cache lines for fine-grained state, the fabric becomes a distributed lock manager.

Better targets:

- VectorDB indexes with compressed address representation;
- graph workloads where frontier ownership is explicit;
- CXL SSD actors that can migrate between device and host;
- runtimes that can choose between local compute, remote memory, and device-side execution.

The kernel and driver layer still matters. It is where address translation, fault handling, page migration, and device trust become real.

## Pages

- `NoC`: on-chip and fabric routing as a coherence problem.
- `PCIe`: PCIe/CXL bridge ideas and P2P data movement.
- `Simulator Design`: why faithful delay injection is hard.
- `runahead`: prediction as a way to pay latency earlier.
