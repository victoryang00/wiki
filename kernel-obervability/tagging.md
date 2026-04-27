# Memory Tagging

Memory tagging is a way to make pointer mistakes visible at the boundary where they become dangerous. The practical idea is simple: carry a small amount of metadata with a pointer or allocation, then check that metadata when the memory is used.

For me the interesting part is not only safety. It is also observability and ownership. A tag can encode which subsystem owns a region, which epoch it belongs to, or whether a device is allowed to touch it.

## Where tags help

- spatial safety: catch a pointer that reaches outside the intended allocation;
- temporal safety: catch use-after-free by changing allocation epochs;
- compartment boundaries: distinguish host, device, sandbox, and runtime-owned memory;
- debugging: make wrong ownership fail close to the bug.

## Why it matters for CXL and runtimes

Once memory can be shared across host, device, and runtime, the address alone is not enough. A pointer can be numerically valid and semantically wrong. Tagging gives us another small handle to encode intent.

The hard part is compatibility. Any tagging scheme has to survive ABI boundaries, DMA, JIT code, and libraries that assume a pointer is just an integer-shaped thing.

1. [Linear Memory Masking](https://news.ycombinator.com/item?id=30865423)
   1. Its usage [Multi-Tag](https://dl.acm.org/doi/fullHtml/10.1145/3579856.3590331)
   2. Sub-page granularity [Sub-page Memory Write Protection](https://asplos.dev/wordpress/2023/11/27/intel-sub-page-write-protection-cai-keng/)
2. [Memory Tagging Extension](https://news.ycombinator.com/item?id=38125379)
