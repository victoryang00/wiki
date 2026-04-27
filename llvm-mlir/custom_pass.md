# Custom Pass

A custom LLVM/MLIR pass is the smallest place where I can inject a systems idea into a program without rewriting the program.

The pass should not be a giant optimizer. It should usually do one of three things:

1. attach metadata that a later layer can use;
2. rewrite a narrow pattern into a runtime call;
3. make an implicit boundary explicit.

## Example: turn an access into an observable access

```mlir
%v = memref.load %A[%i] : memref<?xf32>
```

can become:

```mlir
call @runtime_prefetch_hint(%A, %i) : (memref<?xf32>, index) -> ()
%v = memref.load %A[%i] : memref<?xf32>
```

This looks boring. That is the point. A good pass creates a hook where the runtime can learn, schedule, or migrate, while the original computation stays recognizable.

## Pass design checklist

- What invariant does the pass rely on?
- Does the pass preserve debugability?
- Can the pass be disabled without changing program semantics?
- Is the runtime call on a hot path, and if so, what is the fast path?
- Does the pass introduce target-specific assumptions too early?

## Where I want to use this

- CXL placement hints from access patterns.
- WASM checkpoint and restore barriers.
- GPU/CPU operation fusion boundaries.
- Remote pointer lowering for disaggregated memory.
