# The general purpose usage of inserting bpf and modify state in kernel
## eBPF hardening tool
The Linux kernel has its eBPF verifier that achieves these guarantees by undertaking a strict static analysis across all eBPF programs, checking all paths for invalid memory accesses and disallowing loops to ensure termination. This requires user efforts and a battle with the verifier, which doesn't actually dive into the function-level relations based on synthesis. our work puts the simulation of the process of human battle with the eBPF verifier for LLM to understand. Other hardening tools include Runtime Verifier for inserted eBPF together with other properties that don't fail the static assertion at the runtime.
## Replace UserBypass
## Replace XRP
syscall batching XRP

## Why eBPF for security is wrong

## How dynamic instrumentation works

## Reference
1. https://lore.kernel.org/lkml/202209030333.Goj9I0Pe-lkp@intel.com/T/
2. https://www.kernel.org/doc/html/latest/bpf/index.html