# LLM4Sys4LLM

This section is about using learning and language models for systems work without pretending the model is the system.

The pattern I care about is:

```text
system state -> structured observation -> model proposal -> verifier/runtime check -> action
```

The model can suggest. The system still needs invariants.

## Why systems need this shape

Scheduling, fuzzing, live migration, and debugging all have huge state spaces. Humans write heuristics because exhaustive reasoning is too expensive. LLMs and RL can help search the space, but they should be constrained by compiler facts, kernel state, or formal checks.

## Pages

- `Kernel Fuzzing`: using model-guided generation without losing coverage discipline.
- `LLM with z3`: using solvers as a grounding mechanism for code and policy generation.

## My bias

The best learning system for infrastructure is not the most autonomous one. It is the one that knows when to stop and ask the kernel, compiler, verifier, or runtime for truth.
