# Kernel MM

This section stores my reading notes for Linux memory management. The baseline was Linux 6.4, but the real target is not one version. The target is the mental model: who owns a page, who can reclaim it, who observed it, and how much pain we pay when that answer changes.

I am still learning this subsystem, so treat these pages as working notes. If a claim is wrong, it is probably wrong in an interesting place: locking, lifetime, or policy leaking into mechanism.

## Questions I keep asking

- Where does the ownership of memory live: `mm_struct`, `memcg`, folio, VMA, device driver, or a runtime outside the kernel?
- Which path is policy, and which path is mechanism?
- What can be observed cheaply enough to drive placement?
- When memory becomes remote through CXL or disaggregation, which "local" assumptions quietly break?

## Pages

- `cgroup`: accounting, hierarchy, and resource ownership.
- `rcu`: read-side scaling and lifetime discipline.
- `disaggregation`: remote memory and the cost model behind it.
- `damon`: access monitoring as a placement signal.
