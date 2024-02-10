# Dynamic Program Instrumentation
We currently have such instrumentation techniques:
1. ptrace
2. int 3
3. [syscall intercept](https://github.com/pmem/syscall_intercept) sound disassembler between int 0x80
4. kprobe
5. kretprobe
6. LD_PRELOAD
7. [zpoline](https://www.usenix.org/conference/atc23/presentation/yasukata) use a zero page for trampoline.

# Dynamic GPU ABI Instrumentation
Based upon the GPU call ABI, you can generate a trampoline to intercept the call just like CPU.

AMD CPU has multiple GPU context in the same SMs, while Nvidia need to have persistent kernel to hack the mps. And it's easier to do Dynamic GPU ABI Instrumentation on AMD GPU. The ABI translation can be found in the [CuPBoP-AMD](https://dl.acm.org/doi/fullHtml/10.1145/3624062.3624185).

1. [NVIDIA Nsight Systems](https://developer.nvidia.com/nsight-systems) which leverage CUPTI.
2. [ROCTracer](https://github.com/ROCm/roctracer)
3. [OmniTrace](https://github.com/AMDResearch/omnitrace)
4. NVBIT which leverages PTX JIT

## Reference
1. https://www.youtube.com/watch?v=aC_X0WU-tGM
2. https://www.usenix.org/system/files/atc23_slides_yasukata.pdf