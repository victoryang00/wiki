# WASM

I use WAMR for MVVM development and Wasmer-style fast JIT ideas for DoubleJIT experiments. The reason is not that WASM is trendy. The reason is that WASM gives a compact, portable, inspectable execution state.

That makes it useful for:

- checkpoint and restore;
- live migration;
- sandboxed extension;
- portable runtime instrumentation;
- moving computation between host and device-like environments.

## Why WASM fits my systems taste

WASM is a bytecode, but more importantly it is a state boundary. Linear memory, tables, globals, and stack frames give us a runtime object we can reason about.

The hard part is that real execution is not just WASM state. Once AOT/JIT code enters the picture, we also need to handle native registers, signal state, host calls, TLS, and runtime-owned metadata.

## Pages

- `AoT and JIT`: how runtime compilation changes checkpointing.
- `Linear Memory`: where the apparent simplicity of linear memory starts leaking.
