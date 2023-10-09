## Dynamic better than Static Instrumentation to hook syscall
1. Syscall has semantic meaning, if you are writing a shim layer, only use static instrumentation may break the seccomp garentee for the syscall. 
   1. range write after mmap etc. it will be hand made TOCTOU
   2. if you are using dynamic instrumentation, you can use the semantic meaning of syscall to do the right thing.
2. libcapstone is a dynamic instrumentation tool, it can be used to hook arbritrary assembly. It's better than pin
3. Essentially, syscall intercept discovered that a straightforward approach is sufficient for 0x80 operations within libc. While I've seen that this method isn't universally effective, it's interesting that it's adequate for its specific needs. They utilize 2-byte trampolines to ensure compatibility with syscall instructions. 

## Reference
1. https://asplos.dev/wordpress/2022/05/03/cs225-distributed-kuco-fs-how-libcapstonelibrpmem-can-save-syscalls-for-distributed-fs/
2. https://github.com/pmem/syscall_intercept
3. https://github.com/victoryang00/distributed_kuco_fs/blob/main/badfs-pmem/badfs-intercept/src/lib.rs
4. https://www.intel.com/content/www/us/en/developer/articles/tool/pin-a-dynamic-binary-instrumentation-tool.html