# RTL

I am getting hands-on with RTL because hardware should be part of my systems thinking, not a black box I cite when software runs out of excuses.

The goal is not to become a pure RTL person. The goal is to understand what software is asking the hardware to guarantee.

## What I care about

- delay and buffering as first-class design constraints;
- coherence and fabric management;
- where programmable control can exist without destroying timing;
- how to build enough hardware intuition to design better CXL and accelerator runtimes.

## Pages

- `Delay buffer`: queues, timing, and why buffering is architecture.
- `Fabric manager`: software/hardware coordination for coherent fabrics.
- `Chisel FIRRTL Verilog`: the generator path from idea to emitted hardware.
