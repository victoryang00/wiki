## Perf is powerful
Perf can init bpf, performance counters, kprobes, uprobes, and tracepoints. basically observing the uncore and kernel metrics entry point, wraps all the initial procedure of init bpf jit, msr & set PMU Control register, redirect the PC and hijack the return of kretprobe and partially set ltrace point conditional one instruction. It also wraps the ending procedure of unmap the jit, recover the msr state, and clean the process. The essence of everything is a file manifests in the parameter can be either process-wise or system-wise, all CPU or single CPU. The problem is once you wrap everything into file abstraction, you still need to make sure they might be incorrect because of what. TOUTOC, register cfi, undocumented operations etc.

The perf driver code need the kernel version recognize the chip, etc. when I use 5.4 for alderlake, the expected semantic for perf for little core is non deterministic. When I use 6.0 for SPR, the enable turbo driver seems not be implemented.

## Kernel and CPU preparation of get solid results
```bash
flush_fs_caches()
{
    echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null 2>&1
    sleep 10
}

disable_nmi_watchdog()
{
    echo 0 | sudo tee /proc/sys/kernel/nmi_watchdog >/dev/null 2>&1
}

disable_turbo()
{
    echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo >/dev/null 2>&1
}

# 0: no randomization, everyting is static
# 1: conservative randomization, shared libraries, stack, mmap(), VDSO and heap
# are randomized
# 2: full randomization, the above points in 1 plus brk()
disable_va_aslr()
{
    echo 0 | sudo tee /proc/sys/kernel/randomize_va_space >/dev/null 2>&1
}

disable_swap()
{
    sudo swapoff -a
}

disable_ksm()
{
    echo 0 | sudo tee /sys/kernel/mm/ksm/run >/dev/null 2>&1
}

disable_numa_balancing()
{
    echo 0 | sudo tee /proc/sys/kernel/numa_balancing >/dev/null 2>&1
}

# disable transparent hugepages
disable_thp()
{
    echo "never" | sudo tee /sys/kernel/mm/transparent_hugepage/enabled >/dev/null 2>&1
}

enable_turbo()
{
    echo 0 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo >/dev/null 2>&1
}

disable_ht()
{
    echo off | sudo tee /sys/devices/system/cpu/smt/control >/dev/null 2>&1
}

disable_node1_cpus()
{
    echo 0 | sudo tee /sys/devices/system/node/node1/cpu*/online >/dev/null 2>&1
}

set_performance_mode()
{
    #echo "  ===> Placing CPUs in performance mode ..."
    for governor in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo performance | sudo tee $governor >/dev/null 2>&1
    done
}

disable_node1_mem()
{
    echo 0 | sudo tee /sys/devices/system/node/node1/memory*/online >/dev/null 2>&1
}

# Keep all cores on Node 0 online while keeping all cores on Node 1 offline
disable_node1_core()
{
    echo 0 | sudo tee /sys/devices/system/node/node1/cpu*/online >/dev/null 2>&1
}
```

## The general initial process of perf

```c
PerfInfo::PerfInfo(int group_fd, int cpu, pid_t pid, unsigned long flags, struct perf_event_attr attr)
    : group_fd(group_fd), cpu(cpu), pid(pid), flags(flags), attr(attr) {
    this->fd = perf_event_open(&this->attr, this->pid, this->cpu, this->group_fd, this->flags);
    if (this->fd == -1) {
        LOG(ERROR) << "perf_event_open";
        throw;
    }
    ioctl(this->fd, PERF_EVENT_IOC_RESET, 0);
}
PerfInfo::PerfInfo(int fd, int group_fd, int cpu, pid_t pid, unsigned long flags, struct perf_event_attr attr)
    : fd(fd), group_fd(group_fd), cpu(cpu), pid(pid), flags(flags), attr(attr) {
    this->map = new ThreadSafeMap();
    this->j = std::jthread{[&] { write_trace_to_map(map); }};
}
PerfInfo::~PerfInfo() {
    this->j.join();
    if (this->fd != -1) {
        close(this->fd);
        this->fd = -1;
    }
}
ssize_t PerfInfo::read_pmu(uint64_t *value) {
    ssize_t r = read(this->fd, value, sizeof(*value));
    if (r < 0) {
        LOG(ERROR) << "read";
    }
    return r;
}
int PerfInfo::start() {
    if (ioctl(this->fd, PERF_EVENT_IOC_ENABLE, 0) < 0) {
        LOG(ERROR) << "ioctl";
        return -1;
    }
    return 0;
}
int PerfInfo::stop() {
    if (ioctl(this->fd, PERF_EVENT_IOC_DISABLE, 0) < 0) {
        LOG(ERROR) << "ioctl";
        return -1;
    }
    return 0;
}
```

## Limitation of attaching pmu
Limit to 4, because ctr only has 4 for each cha

## Reference
1. https://github.com/intel/pcm