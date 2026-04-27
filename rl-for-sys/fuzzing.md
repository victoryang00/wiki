## Fuzzing for kernel

Kernel fuzzing is a negotiation with the state space. The fuzzer wants to generate weird inputs. The kernel wants strict structure, privilege, timing, and device state. Most crashes hide behind sequences, not single calls.

## Coverage is necessary but not sufficient

Coverage tells us where the fuzzer went. It does not always tell us whether the path was semantically interesting. For kernel work, a boring path with the right lock ordering can be more valuable than a new basic block in a harmless parser.

The useful signals are:

- syscall or ioctl sequence shape;
- object lifetime transitions;
- privilege boundary changes;
- allocator pressure;
- RCU and lock timing;
- device or filesystem state.

## Where LLMs help

LLMs are good at generating structured families of inputs:

- "make a valid-ish netlink message";
- "mutate this ioctl sequence while preserving handle lifetime";
- "generate a reproducer from this crash log";
- "explain which object probably outlived its owner."

They should not replace the fuzzer. They should feed the fuzzer better grammar, better seeds, and better reducers.

## My preferred loop

```text
coverage + crash + trace
        |
        v
LLM proposes sequence family
        |
        v
fuzzer mutates and executes
        |
        v
sanitizer/verifier/kernel checks truth
```

The model is useful only if the kernel remains the judge.
