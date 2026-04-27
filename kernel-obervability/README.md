# Kernel Observability

Observability is not just "print more counters." For systems work, observability is the act of making a hidden boundary visible without moving the boundary so much that the measurement becomes fiction.

This section is about kernel and runtime instrumentation:

- `rr`: record and replay for performance and device behavior;
- `instrument`: dynamic instrumentation and ABI interception;
- `eBPF`: programmable kernel hooks and the verifier-shaped world;
- `perf`: PMU-driven observation and how easily it lies;
- `tagging`: memory tagging, pointer metadata, and boundary checking.

## My bias

I like observability mechanisms that keep the fast path boring. If the observation path requires global locks, heavyweight traps, or too much semantic reconstruction after the fact, it becomes another system to debug.

The best observability tool answers three questions:

1. What happened?
2. Who owned the state when it happened?
3. Can I act on it before the workload phase has already changed?

That is why eBPF, PMU sampling, record/replay, and device counters belong in the same conversation.
