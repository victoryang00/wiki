## The general purpose usage of inserting bpf and modify state in kernel
I'm leveraging `kretprobe_overwrite_return`, an API was supposed to inject the fault to arbitrary kernel function

### kprobe impl
instrument on any instruction to jmp to `pre_handler`->function
### kretprobe impl
`__kretprobe_trampoline_handler` to hijack the pc to the trampoline code
### uprobe impl
trap the user space instruction to `pre_handler`->function
### bpftime impl
make a map in the userspace and use LLVM JIT to hook the function to write the map, no context switch, no ROB flush
![bpftime](image-1.png)

## eBPF hardening tool
The Linux kernel has its eBPF verifier that achieves these guarantees by undertaking a strict static analysis across all eBPF programs, checking all paths for invalid memory accesses and disallowing loops to ensure termination. This requires user efforts and a battle with the verifier, which doesn't actually dive into the function-level relations based on synthesis. our work puts the simulation of the process of human battle with the eBPF verifier for LLM to understand. Other hardening tools include Runtime Verifier for inserted eBPF together with other properties that don't fail the static assertion at the runtime.
## Replace UserBypass
Compare with SFI way of protecting the boundary, the static compilation with security checks that do not introduce extra checking is always expensive.

## Replace XRP
XRP's idea is syscall batching. We can take the mmaped buffer as a fast pass to User space programming offloading the file system operations to the firmware. IOUring or BPF FUSE has already gotten into the senario, I don't think 

Need data plane in cross boundary communication. control plan in separate U/K.

## Why eBPF for security is wrong
BPF_LSM on loading will enter a previledge mode, it will be hard to maintain the context whether the current thread's permission for memory is complicated, and with page fault or EL1->EL2 change will be hard to maintain

## Reference
1. https://lore.kernel.org/lkml/202209030333.Goj9I0Pe-lkp@intel.com/T/
2. https://www.kernel.org/doc/html/latest/bpf/index.html
3. https://www.youtube.com/watch?v=kvt4wdXEuRU