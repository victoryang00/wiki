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
// mini dumper
void dump_tls(WASMModule *module, WASMModuleInstanceExtra *instance) {
    WASMGlobal *aux_data_end_global = NULL, *aux_heap_base_global = NULL;
    WASMGlobal *aux_stack_top_global = NULL, *global;
    uint32 aux_data_end = (uint32)-1, aux_heap_base = (uint32)-1;
    uint32 aux_stack_top = (uint32)-1, global_index, func_index, i;
    uint32 aux_data_end_global_index = (uint32)-1;
    uint32 aux_heap_base_global_index = (uint32)-1;
    /* Resolve aux stack top global */
    for (int global_index = 0; global_index < instance->global_count; global_index++) {
        auto global = module->globals + global_index;
        if (global->is_mutable /* heap_base and data_end is
                                  not mutable */
            && global->type == VALUE_TYPE_I32 && global->init_expr.init_expr_type == INIT_EXPR_TYPE_I32_CONST &&
            (uint32)global->init_expr.u.i32 <= aux_heap_base) {
            //        LOGV(INFO) << "TLS" << global->init_expr << "\n";
            // this is not the place been accessed, but initialized.
        } else {
            break;
        }
    }
}
```
