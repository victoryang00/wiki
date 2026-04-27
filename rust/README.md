# Rust

Rust is interesting to me because it makes ownership part of the language contract. That does not magically solve systems programming, but it does move many bugs from runtime folklore into compile-time negotiation.

The notes here are about Rust at the boundary:

- FFI and C ABI work;
- OS-specific APIs like Windows io_uring;
- dynamic instrumentation and disassembly;
- virtualization and driver-facing code.

## My rule of thumb

Rust is most valuable when the ownership model is real. If the code is mostly raw pointers, global state, and `unsafe` wrappers around an unstable ABI, Rust still helps, but only if the unsafe boundary is small and honest.

## Pages

- `IORing Windows`: wrapping a kernel API when the binding is not fully exposed.
- `Asahi Virt`: virtualization questions on Apple Silicon.
- `LibCapstone`: dynamic instrumentation and syscall interception.
