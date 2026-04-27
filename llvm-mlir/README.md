# LLVM and MLIR

LLVM is where a lot of systems ideas become real enough to measure. MLIR is where those ideas can stay structured for longer before collapsing into target-specific instructions.

My interest here is not compiler purity. I care about compilers as runtime control planes:

- represent remote pointers and device-owned state;
- lower high-level movement into explicit prefetch, migration, and scheduling decisions;
- make checkpoint and replay visible in IR;
- keep enough structure for heterogeneous execution without hand-writing every backend.

## Pages

- `custom_pass`: how to think about passes as small policy injectors.
- `remotable_pointer`: pointer semantics when data may live across a fabric.
- `mlir`: dialects, lowering, and why structured IR is useful for systems.

## The question I keep asking

Can the compiler preserve enough intent that the runtime does not have to rediscover it with profiling and guesswork?
