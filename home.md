# SlugWiki

This is the scratchpad I wish I had when I started connecting architecture, kernel, compiler, runtime, and accelerator work into one mental model.

The notes are not meant to be a clean textbook. They are closer to lab notes: what abstraction is leaking, what boundary is expensive, what the hardware is actually promising, and where software can still take a swing.

## How to read it

- Start from the layer you already know, then move sideways. CXL only makes sense if you think about paging, cache coherence, PCIe, runtime placement, and workload shape at the same time.
- Treat every page as a working model. If a page says "I think", it means the claim is an engineering hypothesis, not a law of nature.
- The useful question is usually not "can this be accelerated?", but "where does ownership move, who observes it, and what state must survive migration?"

## Current center of gravity

- CXL and disaggregated memory as a system interface, not just a faster remote NUMA node.
- eBPF and instrumentation as a way to expose control-plane truth without rewriting the whole kernel.
- WASM, MLIR, and runtime code generation as portable state machines for moving computation.
- RTL and quantitative architecture as the discipline that keeps software fantasies honest.
