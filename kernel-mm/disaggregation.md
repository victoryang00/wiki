## Motivation

For an orchestration system, **resource management** needs to consider at least the following aspects:

1. An abstraction of the resource model; including,

   - What kinds of resources are there, for example, CPU, memory (local vs remote that can be transparent to the user), etc.;

   - How to represent these resources with data structures;

   - resource scheduling

   - How to describe a resource application (spec) of a workload, for example, "This container requires 4 cores and 12GB~16GB(4GB local/ 8GB-12GB remote) of memory";

   - How to describe the current resource allocation status of a node, such as the amount of allocated/unallocated resources, whether it supports over-segmentation, etc.;

   - **Scheduling algorithm**: how to select the most suitable node for it according to the workload spec;

2. Resource quota

   - How to ensure that the amount of resources used by the workload does not exceed the preset range (so as not to affect other workloads);

   - How to ensure the quota of workload and system/basic service so that the two do not affect each other.

k8s is currently the most popular container orchestration system, so how does it solve these problems?

## **k8s resource model**

Compared with the above questions, let's see how k8s is designed:

1. Resource model
   - Abstract resource types such as cpu/memory/device/hugepage;
   - Abstract the concept of node;
2. Resource Scheduling
   - `request`The two concepts of and are abstracted `limit`, respectively representing the minimum (request) and maximum (limit) resources required by a container;
   - `Allocatable`The scheduling algorithm selects the appropriate node for the container according to the amount of resources currently available for allocation ( ) of each node ; Note that k8s **scheduling only looks at requests, not limits** .
3. Resource enforcement
   - Use cgroups to ensure that the maximum amount of resources used by a workload does not exceed the specified limits at multiple levels.

An example of a resource application (container):

```yaml
apiVersion: v2
kind: Pod
spec:
  containers:
  - name: busybox
    image: busybox
    resources:
      limits:
        cpu: 500m
        memory: "400Mi"
      requests:
        cpu: 250m
        memory: "300Mi"
    command: ["md5sum"]
    args: ["/dev/urandom"]
```

Here requests and `limits` represent the minimum and maximum values of required resources, respectively.

- The unit of CPU resources `m` is `millicores` the abbreviation, which means **one-thousandth of a core**, so `cpu: 500m` means that `0.5` a core is required;
- The unit of memory is well understood, that is, common units such as MB and GB.

### **Node resource abstraction**

```bash
$ k describe node <node>
...
Capacity:
  cpu:                          48
  mem-hard-eviction-threshold:  500Mi
  mem-soft-eviction-threshold:  1536Mi
  memory:                       263192560Ki
  pods:                         256
Allocatable:
  cpu:                 46
  memory:              258486256Ki
  pods:                256
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource            Requests     Limits
  --------            --------     ------
  cpu                 800m (1%)    7200m (15%)
  memory              1000Mi (0%)  7324Mi (2%)
  hugepages-1Gi       0 (0%)       0 (0%)
...
```

Let's look at these parts separately.

### **Capacity**

The total resources of this node (which can be simply understood as **physical configuration** ), for example, the above output shows that this node has 48CPU, 256GB memory, and so on.

### **Allocatable**

**The total amount of resources that can be allocated by k8s** , obviously, Allocatable will not exceed Capacity, for example, there are 2 less CPUs as seen above, and only 46 are left.

### **Allocated**

The amount of resources that this node has allocated so far, note that the message also said that the node **may be oversubscribed** , so the sum may exceed Allocatable, but it will not exceed Capacity.

Allocatable does not exceed Capacity, and this concept is also well understood; but **which resources are allocated specifically** , causing `Allocatable < Capacity`it?

### **Node resource segmentation (reserved)**

Because k8s-related basic services such as kubelet/docker/containerd and other operating system processes such as systemd/journald run on each node, not all resources of a node can be used to create pods for k8s. Therefore, when k8s manages and schedules resources, it needs to separate out the resource usage and enforcement of these basic services.

To this end, k8s proposed the **Node Allocatable Resources[1]** proposal, from which the above terms such as Capacity and Allocatable come from. A few notes:

- If Allocatable is available, the scheduler will use Allocatable, otherwise it will use Capacity;
- Using Allocatable is not overcommit, using Capacity is overcommit;

Calculation formula: **[Allocatable] = [NodeCapacity] - [KubeReserved] - [SystemReserved] - [HardEvictionThreshold]**

Let’s look at these types separately.

### **System Reserved**

Basic services of the operating system, such as systemd, journald, etc., **are outside k8s management** . k8s cannot manage the allocation of these resources, but it can manage the enforcement of these resources, as we will see later.

### **Kube Reserved**

k8s infrastructure services, including kubelet/docker/containerd, etc. Similar to the system services above, k8s cannot manage the allocation of these resources, but it can manage the enforcement of these resources, as we will see later.

### **EvictionThreshold (eviction threshold)**

When resources such as node memory/disk are about to be exhausted, kubelet starts to **expel pods according to the QoS priority (best effort/burstable/guaranteed)** , and eviction resources are reserved for this purpose.

### **Allocatable**

Resources available for k8s to create pods.

The above is the basic resource model of k8s. Let's look at a few related configuration parameters.

### **Kubelet related configuration parameters**

kubelet command parameters related to resource reservation (segmentation):

- `--system-reserved=""`
- `--kube-reserved=""`
- `--qos-reserved=""`
- `--reserved-cpus=""`

It can also be configured via the kubelet, for example,

```
$ cat /etc/kubernetes/kubelet/config
...
systemReserved:
  cpu: "2"  
  memory: "4Gi"
```

Do you need to use a dedicated cgroup for resource quotas for these reserved resources to ensure that they do not affect each other:

- `--kube-reserved-cgroup=""`
- `--system-reserved-cgroup=""`

The default is not enabled. In fact, it is difficult to achieve complete isolation. The consequence is that the system process and the pod process may affect each other. For example, as of v1.26, k8s does not support IO isolation, so the IO of the host process (such as log rotate) soars, or when a pod process executes java dump, It will affect all pods on this node.

The k8s resource model will be introduced here first, and then enter the focus of this article, how k8s uses cgroups to limit the resource usage of workloads such as containers, pods, and basic services (enforcement).

## ## k8s cgroup design

### ### cgroup base

groups are Linux kernel infrastructures that can **limit, record and isolate** the amount of resources (CPU, memory, IO, etc.) **used by** process groups.

There are two versions of cgroup, v1 and v2. For the difference between the two, please refer to **Control Group v2. Since it's already 2023, we focus on v2.** The cgroup v1 exposes more memory stats like swapiness, and all the control is flat control, v2 exposes only cpuset and memory and exposes the hierarchy view.

```bash
$ mount | grep cgroup
cgroup2 on /sys/fs/cgroup type cgroup2 (rw,nosuid,nodev,noexec,relatime,nsdelegate,memory_recursiveprot)

$ root@banana:~/CXLMemSim/microbench# ls /sys/fs/cgroup
cgroup.controllers      cpuset.mems.effective  memory.reclaim
cgroup.max.depth        dev-hugepages.mount    memory.stat
cgroup.max.descendants  dev-mqueue.mount       misc.capacity
cgroup.pressure         init.scope             misc.current
cgroup.procs            io.cost.model          sys-fs-fuse-connections.mount
cgroup.stat             io.cost.qos            sys-kernel-config.mount
cgroup.subtree_control  io.pressure            sys-kernel-debug.mount
cgroup.threads          io.prio.class          sys-kernel-tracing.mount
cpu.pressure            io.stat                system.slice
cpu.stat                memory.numa_stat       user.slice
cpuset.cpus.effective   memory.pressure        yyw

$ root@banana:~/CXLMemSim/microbench# ls /sys/fs/cgroup/yyw
cgroup.controllers      cpu.uclamp.max       memory.oom.group
cgroup.events           cpu.uclamp.min       memory.peak
cgroup.freeze           cpu.weight           memory.pressure
cgroup.kill             cpu.weight.nice      memory.reclaim
cgroup.max.depth        io.pressure          memory.stat
cgroup.max.descendants  memory.current       memory.swap.current
cgroup.pressure         memory.events        memory.swap.events
cgroup.procs            memory.events.local  memory.swap.high
cgroup.stat             memory.high          memory.swap.max
cgroup.subtree_control  memory.low           memory.swap.peak
cgroup.threads          memory.max           memory.zswap.current
cgroup.type             memory.min           memory.zswap.max
cpu.idle                memory.node_limit1   pids.current
cpu.max                 memory.node_limit2   pids.events
cpu.max.burst           memory.node_limit3   pids.max
cpu.pressure            memory.node_limit4   pids.peak
cpu.stat                memory.numa_stat
```

The procfs is registered using the API `cftype` that updates on every access the `memroy.numa_stat`

```c
```

