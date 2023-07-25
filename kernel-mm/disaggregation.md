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

Here, requests and limits represent the minimum and maximum values of required resources.

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

![](https://d33wubrfki0l68.cloudfront.net/21f29e72a3846d4f25c5a33f18cddd09a45a9b34/10990/images/docs/memory-manager-diagram.svg)

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

## k8s cgroup design

### cgroup base

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
anon N0=0 N1=0
file N0=4211032064 N1=13505200128
kernel_stack N0=0 N1=0
pagetables N0=0 N1=0
sec_pagetables N0=0 N1=0
shmem N0=0 N1=0
file_mapped N0=0 N1=0
file_dirty N0=0 N1=0
file_writeback N0=0 N1=0
swapcached N0=0 N1=0
anon_thp N0=0 N1=0
file_thp N0=0 N1=0
shmem_thp N0=0 N1=0
inactive_anon N0=0 N1=0
active_anon N0=0 N1=0
inactive_file N0=4176166912 N1=11106676736
active_file N0=34865152 N1=2398523392
unevictable N0=0 N1=0
slab_reclaimable N0=21441072 N1=19589888
slab_unreclaimable N0=136 N1=0
workingset_refault_anon N0=0 N1=0
workingset_refault_file N0=0 N1=0
workingset_activate_anon N0=0 N1=0
workingset_activate_file N0=0 N1=0
workingset_restore_anon N0=0 N1=0
workingset_restore_file N0=0 N1=0
workingset_nodereclaim N0=0 N1=0
```

Cgroup manager is an interface to support 

In pkg/kubelet/cm/qos_container_manager_linux.go:90 will initialize 2 sub directory in `/sys/fs/cgroup/kubepods/` to control burstable and besteffort qos.

```go
// Top level for Qos containers are created only for Burstable
// and Best Effort classes
qosClasses := map[v1.PodQOSClass]CgroupName{
    v1.PodQOSBurstable:  NewCgroupName(rootContainer, strings.ToLower(string(v1.PodQOSBurstable))),
    v1.PodQOSBestEffort: NewCgroupName(rootContainer, strings.ToLower(string(v1.PodQOSBestEffort))),
}
```

For cgroup container manager, the api are described in `kubelet` as below. every once in a while, even if the cgroup scheduler does nothing, it will 1. periodically check the cgroup memory pod and check whether need to reserve more memory or from one qos group to the other. On calling setMemoryReserve, it will updates `memory.max` in the corresponding pod cgroup path. Other checking stats of cgroup path is defined in `vendor/github.com/google/cadvisor/manager/container.go`

```go
type qosContainerManagerImpl struct {
	sync.Mutex
	qosContainersInfo  QOSContainersInfo
	subsystems         *CgroupSubsystems
	cgroupManager      CgroupManager
	activePods         ActivePodsFunc
	getNodeAllocatable func() v1.ResourceList
	cgroupRoot         CgroupName
	qosReserved        map[v1.ResourceName]int64
}

// CgroupManager allows for cgroup management.
// Supports Cgroup Creation ,Deletion and Updates.
type CgroupManager interface {
	// Create creates and applies the cgroup configurations on the cgroup.
	// It just creates the leaf cgroups.
	// It expects the parent cgroup to already exist.
	Create(*CgroupConfig) error
	// Destroy the cgroup.
	Destroy(*CgroupConfig) error
	// Update cgroup configuration.
	Update(*CgroupConfig) error
	// Validate checks if the cgroup is valid
	Validate(name CgroupName) error
	// Exists checks if the cgroup already exists
	Exists(name CgroupName) bool
	// Name returns the literal cgroupfs name on the host after any driver specific conversions.
	// We would expect systemd implementation to make appropriate name conversion.
	// For example, if we pass {"foo", "bar"}
	// then systemd should convert the name to something like
	// foo.slice/foo-bar.slice
	Name(name CgroupName) string
	// CgroupName converts the literal cgroupfs name on the host to an internal identifier.
	CgroupName(name string) CgroupName
	// Pids scans through all subsystems to find pids associated with specified cgroup.
	Pids(name CgroupName) []int
	// ReduceCPULimits reduces the CPU CFS values to the minimum amount of shares.
	ReduceCPULimits(cgroupName CgroupName) error
	// MemoryUsage returns current memory usage of the specified cgroup, as read from the cgroupfs.
	MemoryUsage(name CgroupName) (int64, error)
	// Get the resource config values applied to the cgroup for specified resource type
	GetCgroupConfig(name CgroupName, resource v1.ResourceName) (*ResourceConfig, error)
	// Set resource config for the specified resource type on the cgroup
	SetCgroupConfig(name CgroupName, resource v1.ResourceName, resourceConfig *ResourceConfig) error
}
```

For memory scheduler in the scheduler, k8s defined:

```go
// Manager interface provides methods for Kubelet to manage pod memory.
type Manager interface {
	// Start is called during Kubelet initialization.
	Start(activePods ActivePodsFunc, sourcesReady config.SourcesReady, podStatusProvider status.PodStatusProvider, containerRuntime runtimeService, initialContainers containermap.ContainerMap) error

	// AddContainer adds the mapping between container ID to pod UID and the container name
	// The mapping used to remove the memory allocation during the container removal
	AddContainer(p *v1.Pod, c *v1.Container, containerID string)

	// Allocate is called to pre-allocate memory resources during Pod admission.
	// This must be called at some point prior to the AddContainer() call for a container, e.g. at pod admission time.
	Allocate(pod *v1.Pod, container *v1.Container) error

	// RemoveContainer is called after Kubelet decides to kill or delete a
	// container. After this call, any memory allocated to the container is freed.
	RemoveContainer(containerID string) error

	// State returns a read-only interface to the internal memory manager state.
	State() state.Reader

	// GetTopologyHints implements the topologymanager.HintProvider Interface
	// and is consulted to achieve NUMA aware resource alignment among this
	// and other resource controllers.
	GetTopologyHints(*v1.Pod, *v1.Container) map[string][]topologymanager.TopologyHint

	// GetPodTopologyHints implements the topologymanager.HintProvider Interface
	// and is consulted to achieve NUMA aware resource alignment among this
	// and other resource controllers.
	GetPodTopologyHints(*v1.Pod) map[string][]topologymanager.TopologyHint

	// GetMemoryNUMANodes provides NUMA nodes that are used to allocate the container memory
	GetMemoryNUMANodes(pod *v1.Pod, container *v1.Container) sets.Int

	// GetAllocatableMemory returns the amount of allocatable memory for each NUMA node
	GetAllocatableMemory() []state.Block

	// GetMemory returns the memory allocated by a container from NUMA nodes
	GetMemory(podUID, containerName string) []state.Block
}
```

