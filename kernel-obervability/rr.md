# Record and Replay
We have an idea of bringing "performance record and replay" onto the table in the CXL world and been supported in the first place inside Arch. 

## Assumption
1. What's the virtualization of CPU?
   1. General Register State.
   2. C State, P State and machine state registers like performance counter.
   3. CPU Extensions abstraction by record and replay. You normally interact with Intel extensions with drivers that maps certain address to it and get the results after callback. Or even you are doing MPX-like style VMEXIT VMENTER. They are actually the same as CXL devices because in the scenario of UCIe, every extension is a device and talk to others through CXL link. the difference is only the cost model of latency and bandwidth.
2. What's the virtualization of memory?
   1. MMU - process abstraction
   2. boundary check
3. What's the virtualization of CXL devices in terms of CPU?
   1. Requests in the CXL link
4. What's the virtualization of CXL devices in terms of outer devices?
   1. VFIO
   2. SRIOV
   3. DDA

## Implementation
1. Bus monitor
   1. CXL Address Translation Service
![ATS](image.png)
2. Possible Implementation
   1. MVVM, we can actually leverage the
   2. J Extension with mmap memory for stall cycles until observed signal