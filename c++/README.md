# C++ Notes

I learned a lot from Barry's blog and from writing enough systems code to be suspicious of both "zero cost" and "modern C++" when they are used as slogans.

My C++ notes here are about the parts that still matter for systems work:

- views and ranges as a way to separate traversal from storage;
- polymorphic memory resources as an explicit allocator interface;
- static reflection and compile-time structure as a way to remove serialization tax;
- ABI boundaries where C++ stops being a language and becomes a contract.

The practical goal is simple: if the program is close to hardware, the ownership model should be visible. If the ownership model is hidden, the cost will come back as cache misses, allocator pressure, or an impossible debugging session.

## Reading order

1. `view` for lazy traversal and why it matters for data movement.
2. `pmr` for allocator control when memory locality is part of correctness.
3. `static replex expr` for compile-time reflection as a serialization and layout tool.
