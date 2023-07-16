# CGroup
First it leverage the procfs to gain update and stats from the kernel. It leverage the hooks in the namespace, which, for example, if you don't want the current cgroup not exceeds the memory.max, root_memcg and your current hierarchy of memcg both have memcg, and the `container_of` operations will get you to the offset of which memcg and read the corresponding memory.max value to limit the memory. Then, RDMA CGroup has abstraction of internal resource pool like `hca_object` and `hca_handle`, while IO CGroup chas limits of rbytes

## V1 vs V2
1. The procfs read write api are different.
```c
{
    .name = "swappiness",
    .read_u64 = mem_cgroup_swappiness_read,
    .write_u64 = mem_cgroup_swappiness_write,
},
static u64 mem_cgroup_swappiness_read(struct cgroup_subsys_state *css,
				      struct cftype *cft)
{
	struct mem_cgroup *memcg = mem_cgroup_from_css(css);

	return mem_cgroup_swappiness(memcg);
}

static int mem_cgroup_swappiness_write(struct cgroup_subsys_state *css,
				       struct cftype *cft, u64 val)
{
	struct mem_cgroup *memcg = mem_cgroup_from_css(css);

	if (val > 200)
		return -EINVAL;

	if (!mem_cgroup_is_root(memcg))
		WRITE_ONCE(memcg->swappiness, val);
	else
		WRITE_ONCE(vm_swappiness, val);

	return 0;
}
```

```c
{
    .name = "oom.group",
    .flags = CFTYPE_NOT_ON_ROOT | CFTYPE_NS_DELEGATABLE,
    .seq_show = memory_oom_group_show,
    .write = memory_oom_group_write,
},
static int memory_oom_group_show(struct seq_file *m, void *v)
{
	struct mem_cgroup *memcg = mem_cgroup_from_seq(m);

	seq_printf(m, "%d\n", READ_ONCE(memcg->oom_group));

	return 0;
}

static ssize_t memory_oom_group_write(struct kernfs_open_file *of,
				      char *buf, size_t nbytes, loff_t off)
{
	struct mem_cgroup *memcg = mem_cgroup_from_css(of_css(of));
	int ret, oom_group;

	buf = strstrip(buf);
	if (!buf)
		return -EINVAL;

	ret = kstrtoint(buf, 0, &oom_group);
	if (ret)
		return ret;

	if (oom_group != 0 && oom_group != 1)
		return -EINVAL;

	WRITE_ONCE(memcg->oom_group, oom_group);

	return nbytes;
}
```
2. multiple hierchy definination vs. single hierarchical tree management.
3. memory ownership and memory swap events
4. eBPF and rootless containers
## Lifetime of a cgroup

![cgroup lifetime](https://image.whysdomain.com/jksj/qtlinuxcgroup01.png)

## Migration on demand
https://lwn.net/Articles/916583/

## How to get the struct what you want memcg etc. in kernel
I have to get memcg from the current pid.
1. If it's located in the task struct scope, simply use the `current` for getting the struct `get_mem_cgroup_from_mm(current->mm)`.
2. If you are in the `work_struct`, you are possibly get struct by argument passing or `container_of` or back pointer.

It's hard to get something in the critical path because it always acquires locks or rcu for getting some struct to be multithread safe. But there's always performance work around hacks.