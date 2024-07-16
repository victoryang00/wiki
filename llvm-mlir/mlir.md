# Dialect
Higher level IRs are defined as dialects.

Dialect->Operation
## scf
structured control flow
```c++
scf.for %i = 0 to 128 step %c1 {
  %y = scf.execute_region -> i32 {
    %x = load %A[%i] : memref<128xi32>
    scf.yield %x : i32
  }
}
```
better form for 
## MLIR JIT
mlir-cpu-runner

## Reference
1. [使用MLIR完成一个端到端的编译流程 -- 一条通路](https://zhuanlan.zhihu.com/p/328993481)