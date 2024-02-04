The WAMR memory is maintained in 1. Module Instance structure: WAMR maintains the module instance data using C struct “WASMModuleInstance”.
2. function data: contain the function instances and a few pointer arrays that refer to the native function, function type and imported functions
3. linear memory: the memory for the linear memory data space and associated information
4. global data: the memory for the data of Wasm globals and associated information
5. exports:
6. tables:
7. WASI context
8. WASI-NN context

## The impact of linear memory
Every memory ptr is the offset to the mmap first address. In interpreter the loader will malloc the memory. In AOT, the memory is mmaped and the offset is the offset to the mmaped address. 

Other than linear memory, we have multiple memory regions for the global data, the table data, the function data, and the module instance data. The memory regions are either mmaped or malloced and mantained by linker and loader which is largely OS and libc specific.

## InterpFrame, JITFrame & AOTFrame
The current WAMR frame model is implemented in a unified view after [PR #2830](). Whereas on each of WebAssembly branch, the native view will commit the register to the stack without going into the unified WASM Frame.