# Read! Copy! Update!
When it comes to multithreaded programming, everyone can think of locking, such as user-state `pthread_mutex_lock/unlock` and kernel-state `mutex_lock/spin_lock` locking mechanisms. The common feature of these mechanisms is that they treat any party that adds a lock fairly. The variable decorated by RCU can hold the **reader biased** lock primitive for the variable.

![](https://www.kernel.org/doc/Documentation/RCU/Design/Expedited-Grace-Periods/ExpRCUFlow.svg)

1. Read the variable with read-side critical section.
2. The grace period is started by the writer until the CPU reports the CPU quiescent state. The writer protected critical section should be serializable.

```c
void read(void)
{
    rcu_read_lock();
    // read the variable
    rcu_read_unlock();
}

void write(void)
{
    struct user *new = malloc(struct user);
    struct uer *old = user_table[i];

    memcpy(new, old, sizeof(struct user));

    user_table[i] = new;
    // don't care reads the new or old, grace point
    synchronize_rcu();
    free(old);
}
```

## Drawbacks
1. RCU has starvation problem. The writer can be starved by the reader. The writer can be starved by the reader.
2. Although RCU readers and writers are always allowed to access a shared data, writers are not allowed to free dynamically allocated data that was modified before the end of the grace-period. The end of a grace period ensures that no readers are accessing the old version of dynamically allocated shared data, allowing writers to return the memory to the system safely. Hence, a drawback of RCU is that a long wait for the end of a grace period can lead the system to run out-of-memory.