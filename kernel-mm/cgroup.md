# V1 vs V2
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