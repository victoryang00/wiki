## GPU virt

GPU virtualization on Apple Silicon is interesting because the hardware/software stack was not designed around the same public virtualization contracts as a typical x86 server GPU setup.

The hard part is not only "can I expose a GPU to a guest?" It is:

- what memory objects does the GPU see;
- who owns command submission;
- how faults and synchronization are reported;
- whether the host can safely multiplex contexts.

## Asahi KVM

Asahi Linux gives us a rare chance to watch a modern client SoC become understandable from the outside. KVM support is not just a checkbox. It means defining enough architectural state that a guest can run while the host keeps control of interrupts, timers, memory, and devices.

For systems work, the interesting question is what becomes virtualizable as an architectural interface, and what remains a driver convention.

## Why MacOS did not adopt KVM and eBPF?

My read: macOS tends to expose higher-level frameworks instead of Linux-style programmable kernel mechanisms. KVM and eBPF both expose low-level extensibility. That is powerful, but it makes verification, security policy, and product compatibility much harder.

Linux accepts that tradeoff because infrastructure users need hooks. Apple usually prefers a smaller surface with stronger control.

For research, this contrast is useful. It shows two different philosophies:

- Linux: expose mechanisms, let users build policy.
- macOS: expose curated policy, keep mechanisms private.

## Reference
1. https://www.reddit.com/r/AsahiLinux/comments/y7hplo/virtual_machines_on_asahi_linux/
