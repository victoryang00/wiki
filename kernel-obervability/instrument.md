# Dynamic Program Instrumentation
We currently have such instrumentation techniques:
1. ptrace
2. int 3
3. [syscall intercept](https://github.com/pmem/syscall_intercept) sound disassembler between int 0x80
4. kprobe
5. kretprobe
6. LD_PRELOAD
7. [zpoline](https://www.usenix.org/conference/atc23/presentation/yasukata) use a zero page for trampoline.

# Static GPU ABI Instrumentation
1. [NVIDIA Nsight Systems](https://developer.nvidia.com/nsight-systems)
2. [AMD CodeXL](https://gpuopen.com/compute-product/codexl/)
3. NVBIT

## Reference
1. https://www.youtube.com/watch?v=aC_X0WU-tGM
2. https://www.usenix.org/system/files/atc23_slides_yasukata.pdf