# What if I want to slow the memory down to 3us and what will happen in the modern CPU?


1. The Demysifying paper does not give any information of the ROB and MSHR which says nothing, we need to answer this question to understand the workload better.
2. If they were the first to make the delay buffer, I have some other things to ask and answer.
   1. For a serial linkage through CXL, how do we view delayed buffer? Is this remote ROB?
   2. If we have a remote ROB, how do we view the local ROB?
   3. How do we codesign the MSHR and ROB for less address translation like offloading AGU?
3. I think in the latest CPU, the ROB and MSHR are not the same thing, and the ROB is not the same thing as the delay buffer. For the workload, the decision to learn is from those two latency model.