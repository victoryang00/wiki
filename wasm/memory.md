The WAMR memory is maintained in 1. Module Instance structure: WAMR maintains the module instance data using C struct “WASMModuleInstance”.
2. function data: contain the function instances and a few pointer arrays that refer to the native function, function type and imported functions
3. linear memory: the memory for the linear memory data space and associated information
4. global data: the memory for the data of Wasm globals and associated information
5. exports:
6. tables:
7. WASI context
8. WASI-NN context
## The impact of linear memory


Every memory ptr is the offset to the mmap first address, in interpreter the loader will malloc the 
```c
[data end]
```