## IOURing for Windows
ntdll.dll is not fully exposed into the [windows-rs](https://github.com/microsoft/windows-rs). So we need C binding for getting the io_uring sqe and cqe.

```bash
pdbex.exe * ntkrnlmp.pdb -o ntkrnlmp.h
```

We found the cpp wrapped API with the following signature:

```cpp
HRESULT win_ring_queue_init(_In_ uint32_t entries,
                            _Out_ struct win_ring *ring) {
  NT_IORING_STRUCTV1 ioringStruct = {
      .IoRingVersion = IORING_VERSION_3, // Requires Win11 22H2
      .SubmissionQueueSize = entries,
      .CompletionQueueSize = entries * 2,
      .Flags = {
          .Required = NT_IORING_CREATE_REQUIRED_FLAG_NONE,
          .Advisory = NT_IORING_CREATE_ADVISORY_FLAG_NONE,
      }};
  NTSTATUS status =
      NtCreateIoRing(&ring->handle, sizeof(ioringStruct), &ioringStruct,
                     sizeof(ring->info), &ring->info);
  return HRESULT_FROM_NT(status);
};
```

Originally, we want to fully move this to rust with c pod definition, but cqe's return value from windows kernel is always wrong, if we wrap the unsafe. We thought is the ptr updates is stale and takes the wrong value. So we have to use the c binding for now.