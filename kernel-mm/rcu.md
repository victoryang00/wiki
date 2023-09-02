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
1. RCU has starvation problem. 
2. Although RCU readers and writers are always allowed to access a shared data, writers are not allowed to free dynamically allocated data that was modified before the end of the grace-period. The end of a grace period ensures that no readers are accessing the old version of dynamically allocated shared data, allowing writers to return the memory to the system safely. Hence, a drawback of RCU is that a long wait for the end of a grace period can lead the system to run out-of-memory.

## Pitfalls
```bash
[  +6.019620] ------------[ cut here ]------------
[  +0.000004] Voluntary context switch within RCU read-side critical section!
[  +0.000004] WARNING: CPU: 12 PID: 1010 at kernel/rcu/tree_plugin.h:320 rcu_note_context_switch+0x43d/0x560
[  +0.000009] Modules linked in: xt_CHECKSUM ipt_REJECT nf_reject_ipv4 xt_tcpudp nft_chain_nat rpcsec_gss_krb5 auth_rpcgss xt_MASQUERADE nf_nat nf_conntrack_netlink xfrm_user xfrm_algo xt_addrtype br_netfilter bridge stp llc nfsv4 nfs lockd grace fscache netfs xt_conntrack nf_conntrack nf_defrag_ipv6 nf_defrag_ipv4 xt_comment nft_compat nf_tables nfnetlink binfmt_misc sunrpc intel_rapl_msr intel_rapl_common intel_uncore_frequency intel_uncore_frequency_common i10nm_edac nfit x86_pkg_temp_thermal intel_powerclamp coretemp kvm_intel nls_iso8859_1 pmt_telemetry kvm pmt_class intel_sdsi irqbypass cmdlinepart rapl intel_cstate spi_nor idxd input_leds mei_me isst_if_mbox_pci isst_if_mmio mtd intel_vsec isst_if_common idxd_bus mei ipmi_ssif acpi_ipmi ipmi_si ipmi_devintf ipmi_msghandler acpi_power_meter acpi_pad mac_hid pfr_update pfr_telemetry sch_fq_codel dm_multipath scsi_dh_rdac scsi_dh_emc scsi_dh_alua msr pstore_blk ramoops reed_solomon pstore_zone efi_pstore ip_tables x_tables autofs4 btrfs blake2b_generic raid10
[  +0.000065]  raid456 async_raid6_recov async_memcpy async_pq async_xor async_tx xor raid6_pq libcrc32c raid1 raid0 multipath linear hid_generic usbhid rndis_host hid cdc_ether usbnet igb crct10dif_pclmul nvme crc32_pclmul drm_shmem_helper polyval_clmulni polyval_generic drm_kms_helper nvme_core ghash_clmulni_intel sha512_ssse3 aesni_intel dax_hmem cxl_acpi ahci drm cxl_core crypto_simd cryptd dca spi_intel_pci nvme_common libahci i2c_i801 xhci_pci i2c_algo_bit spi_intel i2c_ismt i2c_smbus xhci_pci_renesas wmi pinctrl_emmitsburg
[  +0.000038] CPU: 12 PID: 1010 Comm: kworker/u193:11 Tainted: G S                 6.4.0+ #39
[  +0.000003] Hardware name: Supermicro SYS-621C-TN12R/X13DDW-A, BIOS 1.1 02/02/2023
[  +0.000002] Workqueue: writeback wb_workfn (flush-259:0)
[  +0.000008] RIP: 0010:rcu_note_context_switch+0x43d/0x560
[  +0.000004] Code: 00 48 89 be 40 08 00 00 48 89 86 48 08 00 00 48 89 10 e9 63 fe ff ff 48 c7 c7 d0 cd 94 82 c6 05 a6 ac 41 02 01 e8 73 1b f3 ff <0f> 0b e9 27 fc ff ff a9 ff ff ff 7f 0f 84 cf fc ff ff 65 48 8b 3c
[  +0.000002] RSP: 0018:ffa00000203674a8 EFLAGS: 00010046
[  +0.000003] RAX: 0000000000000000 RBX: ff11001fff733640 RCX: 0000000000000000
[  +0.000003] RDX: 0000000000000000 RSI: 0000000000000000 RDI: 0000000000000000
[  +0.000001] RBP: ffa00000203674c8 R08: 0000000000000000 R09: 0000000000000000
[  +0.000001] R10: 0000000000000000 R11: 0000000000000000 R12: 0000000000000000
[  +0.000001] R13: 0000000000000000 R14: ff110001ce730000 R15: ff110001ce730000
[  +0.000001] FS:  0000000000000000(0000) GS:ff11001fff700000(0000) knlGS:0000000000000000
[  +0.000002] CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
[  +0.000002] CR2: 000000c0007da000 CR3: 0000000007a3a004 CR4: 0000000000771ee0
[  +0.000002] DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
[  +0.000001] DR3: 0000000000000000 DR6: 00000000fffe07f0 DR7: 0000000000000400
[  +0.000001] PKRU: 55555554
[  +0.000002] Call Trace:
[  +0.000002]  <TASK>
[  +0.000003]  ? show_regs+0x72/0x90
[  +0.000008]  ? rcu_note_context_switch+0x43d/0x560
[  +0.000002]  ? __warn+0x8d/0x160
[  +0.000007]  ? rcu_note_context_switch+0x43d/0x560
[  +0.000002]  ? report_bug+0x1bb/0x1d0
[  +0.000008]  ? handle_bug+0x46/0x90
[  +0.000006]  ? exc_invalid_op+0x19/0x80
[  +0.000003]  ? asm_exc_invalid_op+0x1b/0x20
[  +0.000006]  ? rcu_note_context_switch+0x43d/0x560
[  +0.000002]  ? rcu_note_context_switch+0x43d/0x560
[  +0.000002]  __schedule+0xb9/0x15f0
[  +0.000006]  ? blk_mq_flush_plug_list+0x19d/0x5e0
[  +0.000007]  ? __blk_flush_plug+0xe9/0x130
[  +0.000005]  schedule+0x68/0x110
[  +0.000004]  io_schedule+0x46/0x80
[  +0.000004]  ? __pfx_wbt_inflight_cb+0x10/0x10
[  +0.000005]  rq_qos_wait+0xd0/0x170
[  +0.000006]  ? __pfx_wbt_cleanup_cb+0x10/0x10
[  +0.000003]  ? __pfx_rq_qos_wake_function+0x10/0x10
[  +0.000003]  ? __pfx_wbt_inflight_cb+0x10/0x10
[  +0.000004]  wbt_wait+0xa8/0x100
[  +0.000003]  __rq_qos_throttle+0x25/0x40
[  +0.000003]  blk_mq_submit_bio+0x291/0x660
[  +0.000004]  __submit_bio+0xb3/0x1c0
[  +0.000004]  submit_bio_noacct_nocheck+0x2ce/0x390
[  +0.000004]  submit_bio_noacct+0x20a/0x560
[  +0.000003]  submit_bio+0x6c/0x80
[  +0.000003]  ext4_bio_write_folio+0x2d9/0x6a0
[  +0.000006]  ? folio_clear_dirty_for_io+0x148/0x1e0
[  +0.000005]  mpage_submit_folio+0x91/0xc0
[  +0.000008]  mpage_process_page_bufs+0x181/0x1b0
[  +0.000004]  mpage_prepare_extent_to_map+0x1fb/0x570
[  +0.000004]  ext4_do_writepages+0x4bd/0xd80
[  +0.000005]  ext4_writepages+0xb8/0x1a0
[  +0.000003]  do_writepages+0xd0/0x1b0
[  +0.000004]  ? __wb_calc_thresh+0x3e/0x130
[  +0.000003]  __writeback_single_inode+0x44/0x360
[  +0.000002]  writeback_sb_inodes+0x22f/0x500
[  +0.000004]  __writeback_inodes_wb+0x56/0xf0
[  +0.000003]  wb_writeback+0x12b/0x2c0
[  +0.000002]  wb_workfn+0x2dc/0x4e0
[  +0.000003]  ? __schedule+0x3dd/0x15f0
[  +0.000003]  ? add_timer+0x20/0x40
[  +0.000006]  process_one_work+0x229/0x450
[  +0.000006]  worker_thread+0x50/0x3f0
[  +0.000003]  ? __pfx_worker_thread+0x10/0x10
[  +0.000002]  kthread+0xf4/0x130
[  +0.000006]  ? __pfx_kthread+0x10/0x10
[  +0.000003]  ret_from_fork+0x29/0x50
[  +0.000007]  </TASK>
[  +0.000001] ---[ end trace 0000000000000000 ]---
dmesg -wH[  +4.088043] audit: type=1400 audit(1690245681.539:137): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1608723/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
^A[ +10.108572] audit: type=1400 audit(1690245691.647:138): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1617988/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.125741] audit: type=1400 audit(1690245701.775:139): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618033/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.107064] audit: type=1400 audit(1690245711.879:140): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618070/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[Jul25 00:42] audit: type=1400 audit(1690245721.998:141): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618107/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.109829] audit: type=1400 audit(1690245732.106:142): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618136/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[  +5.361027] rcu: INFO: rcu_preempt detected stalls on CPUs/tasks:
[  +0.000005] rcu:      Tasks blocked on level-1 rcu_node (CPUs 0-15): P1010/3:b..l
[  +0.000009] rcu:      (detected by 95, t=15002 jiffies, g=122497, q=1257526 ncpus=96)
[  +0.000006] task:kworker/u193:11 state:I stack:0     pid:1010  ppid:2      flags:0x00004000
[  +0.000004] Workqueue:  0x0 (events_power_efficient)
[  +0.000006] Call Trace:
[  +0.000002]  <TASK>
[  +0.000003]  __schedule+0x3d5/0x15f0
[  +0.000008]  ? add_timer+0x20/0x40
[  +0.000006]  ? queue_delayed_work_on+0x6e/0x80
[  +0.000004]  ? fb_flashcursor+0x159/0x1d0
[  +0.000004]  ? __pfx_bit_cursor+0x10/0x10
[  +0.000002]  schedule+0x68/0x110
[  +0.000003]  worker_thread+0xbd/0x3f0
[  +0.000002]  ? __pfx_worker_thread+0x10/0x10
[  +0.000002]  kthread+0xf4/0x130
[  +0.000003]  ? __pfx_kthread+0x10/0x10
[  +0.000003]  ret_from_fork+0x29/0x50
[  +0.000005]  </TASK>
[  +4.746203] audit: type=1400 audit(1690245742.213:143): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618184/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.110853] audit: type=1400 audit(1690245752.329:144): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618273/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.104983] audit: type=1400 audit(1690245762.433:145): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618325/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.106410] audit: type=1400 audit(1690245772.536:146): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618353/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[Jul25 00:43] audit: type=1400 audit(1690245782.648:147): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618381/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[  +3.181659] bash: page allocation failure: order:0, mode:0x400dc0(GFP_KERNEL_ACCOUNT|__GFP_ZERO), nodemask=0,cpuset=user.slice,mems_allowed=0-1
[  +0.000011] CPU: 78 PID: 1618437 Comm: bash Tainted: G S      W          6.4.0+ #39
[  +0.000003] Hardware name: Supermicro SYS-621C-TN12R/X13DDW-A, BIOS 1.1 02/02/2023
[  +0.000001] Call Trace:
[  +0.000003]  <TASK>
[  +0.000003]  dump_stack_lvl+0x48/0x70
[  +0.000007]  dump_stack+0x10/0x20
[  +0.000001]  warn_alloc+0x14b/0x1c0
[  +0.000006]  __alloc_pages+0x117f/0x1210
[  +0.000004]  ? __mod_lruvec_page_state+0xa0/0x160
[  +0.000004]  ? bede_flush_node_rss+0x77/0x150
[  +0.000004]  alloc_pages+0x95/0x1a0
[  +0.000002]  pte_alloc_one+0x18/0x50
[  +0.000005]  do_fault+0x20a/0x3e0
[  +0.000003]  __handle_mm_fault+0x6ca/0xc70
[  +0.000004]  handle_mm_fault+0xe9/0x350
[  +0.000002]  do_user_addr_fault+0x225/0x6c0
[  +0.000002]  exc_page_fault+0x84/0x1b0
[  +0.000004]  asm_exc_page_fault+0x27/0x30
[  +0.000004] RIP: 0033:0x560e5fcc8d29
[  +0.000003] Code: 8b 3c 24 4c 8b 54 24 08 0f b6 54 24 28 48 8b 30 31 c0 8d 4f 02 48 63 c9 66 0f 1f 84 00 00 00 00 00 41 89 c0 0f b6 c2 8d 79 ff <0f> b7 04 46 66 c1 e8 03 83 e0 01 80 fa 5f 0f 94 c2 08 d0 0f 84 8e
[  +0.000001] RSP: 002b:00007ffea31bac80 EFLAGS: 00010246
[  +0.000002] RAX: 0000000000000073 RBX: 00007ffea31badbc RCX: 0000000000000002
[  +0.000002] RDX: 0000000000000073 RSI: 00007f61b221982c RDI: 0000000000000001
[  +0.000000] RBP: 0000560e60f3d360 R08: 0000000000000000 R09: 0000560e5fd72a3c
[  +0.000001] R10: 0000560e60f3d361 R11: 00007ffea31badb4 R12: 0000000000000001
[  +0.000001] R13: 0000560e60f3d360 R14: 0000000000000000 R15: 0000000000000001
[  +0.000002]  </TASK>
[  +0.000001] Mem-Info:
[  +0.000010] active_anon:716 inactive_anon:214225 isolated_anon:0
               active_file:2383940 inactive_file:3365237 isolated_file:0
               unevictable:6921 dirty:4 writeback:0
               slab_reclaimable:218619 slab_unreclaimable:225558
               mapped:135395 shmem:720 pagetables:6282
               sec_pagetables:0 bounce:0
               kernel_misc_reclaimable:0
               free:59304993 free_pcp:43676 free_cma:0
[  +0.000004] Node 0 active_anon:1836kB inactive_anon:541260kB active_file:4060952kB inactive_file:7522280kB unevictable:4944kB isolated(anon):0kB isolated(file):0kB mapped:353180kB dirty:12kB writeback:0kB shmem:1852kB shmem_thp: 0kB shmem_pmdmapped: 0kB anon_thp: 0kB writeback_tmp:0kB kernel_stack:14472kB pagetables:17076kB sec_pagetables:0kB all_unreclaimable? no
[  +0.000005] Node 0 DMA free:11304kB boost:0kB min:4kB low:16kB high:28kB reserved_highatomic:0KB active_anon:0kB inactive_anon:0kB active_file:0kB inactive_file:0kB unevictable:0kB writepending:0kB present:15992kB managed:15400kB mlocked:0kB bounce:0kB free_pcp:0kB local_pcp:0kB free_cma:0kB
[  +0.000004] lowmem_reserve[]: 0 1611 128577 128577 128577
[  +0.000005] Node 0 DMA32 free:1644984kB boost:0kB min:564kB low:2212kB high:3860kB reserved_highatomic:0KB active_anon:0kB inactive_anon:28kB active_file:0kB inactive_file:0kB unevictable:0kB writepending:0kB present:1779904kB managed:1658912kB mlocked:0kB bounce:0kB free_pcp:9184kB local_pcp:0kB free_cma:0kB
[  +0.000003] lowmem_reserve[]: 0 0 126966 126966 126966
[  +0.000005] Node 0 Normal free:116203888kB boost:0kB min:44556kB low:174568kB high:304580kB reserved_highatomic:0KB active_anon:1836kB inactive_anon:541232kB active_file:4060952kB inactive_file:7522280kB unevictable:4944kB writepending:12kB present:132120576kB managed:130013316kB mlocked:4944kB bounce:0kB free_pcp:165500kB local_pcp:1048kB free_cma:0kB
[  +0.000004] lowmem_reserve[]: 0 0 0 0 0
[  +0.000003] Node 0 DMA: 2*4kB (U) 2*8kB (U) 1*16kB (U) 0*32kB 0*64kB 0*128kB 0*256kB 0*512kB 1*1024kB (U) 1*2048kB (M) 2*4096kB (M) = 11304kB
[  +0.000009] Node 0 DMA32: 6*4kB (UM) 7*8kB (UM) 4*16kB (UM) 9*32kB (UM) 4*64kB (UM) 6*128kB (UM) 6*256kB (UM) 10*512kB (UM) 9*1024kB (M) 9*2048kB (UM) 393*4096kB (M) = 1645488kB
[  +0.000010] Node 0 Normal: 515*4kB (UME) 5*8kB (UME) 31*16kB (ME) 13*32kB (ME) 29*64kB (UME) 33*128kB (ME) 25*256kB (ME) 10*512kB (M) 3*1024kB (UME) 0*2048kB 28364*4096kB (UM) = 116202628kB
[  +0.000011] Node 0 hugepages_total=0 hugepages_free=0 hugepages_surp=0 hugepages_size=1048576kB
[  +0.000001] Node 0 hugepages_total=0 hugepages_free=0 hugepages_surp=0 hugepages_size=2048kB
[  +0.000001] 5750183 total pagecache pages
[  +0.000001] 0 pages in swap cache
[  +0.000001] Free swap  = 0kB
[  +0.000000] Total swap = 0kB
[  +0.000001] 67033550 pages RAM
[  +0.000000] 0 pages HighMem/MovableOnly
[  +0.000001] 1086155 pages reserved
[  +0.000001] 0 pages hwpoisoned
[  +0.000001] Huh VM_FAULT_OOM leaked out to the #PF handler. Retrying PF
[  +6.926681] audit: type=1400 audit(1690245792.756:148): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618513/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.107864] audit: type=1400 audit(1690245802.860:149): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618587/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.105275] audit: type=1400 audit(1690245812.967:150): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618650/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.109661] audit: type=1400 audit(1690245823.075:151): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618680/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[  +8.500616] audit: type=1400 audit(1690245831.575:152): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618740/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[  +1.607178] audit: type=1400 audit(1690245833.183:153): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618752/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0

[Jul25 00:44] audit: type=1400 audit(1690245843.287:154): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618812/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.121376] audit: type=1400 audit(1690245853.411:155): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618883/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.109163] audit: type=1400 audit(1690245863.519:156): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1618986/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[  +3.110811] INFO: task systemd:1 blocked for more than 120 seconds.
[  +0.000004]       Tainted: G S      W          6.4.0+ #39
[  +0.000001] "echo 0 > /proc/sys/kernel/hung_task_timeout_secs" disables this message.
[  +0.000001] task:systemd         state:D stack:0     pid:1     ppid:0      flags:0x00000002
[  +0.000003] Call Trace:
[  +0.000002]  <TASK>
[  +0.000003]  __schedule+0x3d5/0x15f0
[  +0.000008]  schedule+0x68/0x110
[  +0.000002]  schedule_timeout+0x151/0x160
[  +0.000004]  ? get_page_from_freelist+0x6a4/0x1450
[  +0.000005]  __wait_for_common+0x8f/0x190
[  +0.000003]  ? __pfx_schedule_timeout+0x10/0x10
[  +0.000002]  wait_for_completion+0x24/0x40
[  +0.000003]  __wait_rcu_gp+0x137/0x140
[  +0.000004]  synchronize_rcu+0x10b/0x120
[  +0.000002]  ? __pfx_call_rcu_hurry+0x10/0x10
[  +0.000002]  ? __pfx_wakeme_after_rcu+0x10/0x10
[  +0.000002]  rcu_sync_enter+0x58/0xf0
[  +0.000002]  ? _kstrtoull+0x3b/0xa0
[  +0.000004]  percpu_down_write+0x2b/0x1d0
[  +0.000002]  cgroup_procs_write_start+0x105/0x180
[  +0.000003]  __cgroup_procs_write+0x5d/0x180
[  +0.000002]  cgroup_procs_write+0x17/0x30
[  +0.000002]  cgroup_file_write+0x8c/0x190
[  +0.000003]  ? __check_object_size+0x2a3/0x310
[  +0.000005]  kernfs_fop_write_iter+0x153/0x1e0
[  +0.000004]  vfs_write+0x2cf/0x400
[  +0.000004]  ksys_write+0x67/0xf0
[  +0.000001]  __x64_sys_write+0x19/0x30
[  +0.000001]  do_syscall_64+0x59/0x90
[  +0.000004]  ? count_memcg_events.constprop.0+0x2a/0x50
[  +0.000004]  ? handle_mm_fault+0x1e7/0x350
[  +0.000002]  ? exit_to_user_mode_prepare+0x39/0x190
[  +0.000005]  ? irqentry_exit_to_user_mode+0x9/0x20
[  +0.000002]  ? irqentry_exit+0x43/0x50
[  +0.000001]  ? exc_page_fault+0x95/0x1b0
[  +0.000002]  entry_SYSCALL_64_after_hwframe+0x6e/0xd8
[  +0.000002] RIP: 0033:0x7f9a68314a6f
[  +0.000002] RSP: 002b:00007fffd0e52350 EFLAGS: 00000293 ORIG_RAX: 0000000000000001
[  +0.000002] RAX: ffffffffffffffda RBX: 0000000000000008 RCX: 00007f9a68314a6f
[  +0.000001] RDX: 0000000000000008 RSI: 00007fffd0e5250a RDI: 0000000000000019
[  +0.000001] RBP: 00007fffd0e5250a R08: 0000000000000000 R09: 00007fffd0e52390
[  +0.000001] R10: 0000000000000000 R11: 0000000000000293 R12: 0000000000000008
[  +0.000001] R13: 00005644ec569cb0 R14: 00007f9a68415a00 R15: 0000000000000008
[  +0.000002]  </TASK>
[  +0.000095] INFO: task systemd-journal:1199 blocked for more than 120 seconds.
[  +0.000002]       Tainted: G S      W          6.4.0+ #39
[  +0.000000] "echo 0 > /proc/sys/kernel/hung_task_timeout_secs" disables this message.
[  +0.000001] task:systemd-journal state:D stack:0     pid:1199  ppid:1      flags:0x00000002
[  +0.000002] Call Trace:
[  +0.000001]  <TASK>
[  +0.000001]  __schedule+0x3d5/0x15f0
[  +0.000003]  ? __mod_memcg_lruvec_state+0x8f/0x130
[  +0.000003]  schedule+0x68/0x110
[  +0.000003]  schedule_preempt_disabled+0x15/0x30
[  +0.000002]  __mutex_lock.constprop.0+0x3d8/0x770
[  +0.000002]  __mutex_lock_slowpath+0x13/0x20
[  +0.000002]  mutex_lock+0x3e/0x50
[  +0.000001]  proc_cgroup_show+0x4c/0x450
[  +0.000002]  proc_single_show+0x53/0xe0
[  +0.000004]  seq_read_iter+0x132/0x4e0
[  +0.000004]  seq_read+0xa5/0xe0
[  +0.000003]  vfs_read+0xb1/0x320
[  +0.000002]  ? __seccomp_filter+0x3df/0x5e0
[  +0.000003]  ksys_read+0x67/0xf0
[  +0.000002]  __x64_sys_read+0x19/0x30
[  +0.000001]  do_syscall_64+0x59/0x90
[  +0.000003]  ? exit_to_user_mode_prepare+0x39/0x190
[  +0.000003]  ? syscall_exit_to_user_mode+0x2a/0x50
[  +0.000002]  ? do_syscall_64+0x69/0x90
[  +0.000002]  ? do_syscall_64+0x69/0x90
[  +0.000002]  ? syscall_exit_to_user_mode+0x2a/0x50
[  +0.000002]  ? do_syscall_64+0x69/0x90
[  +0.000002]  ? do_syscall_64+0x69/0x90
[  +0.000002]  entry_SYSCALL_64_after_hwframe+0x6e/0xd8
[  +0.000001] RIP: 0033:0x7f5106d149cc
[  +0.000001] RSP: 002b:00007ffe61c321c0 EFLAGS: 00000246 ORIG_RAX: 0000000000000000
[  +0.000002] RAX: ffffffffffffffda RBX: 0000564ccf0b8210 RCX: 00007f5106d149cc
[  +0.000001] RDX: 0000000000000400 RSI: 0000564ccf0b7b10 RDI: 0000000000000024
[  +0.000001] RBP: 00007f5106e16600 R08: 0000000000000000 R09: 0000000000000001
[  +0.000000] R10: 0000000000001000 R11: 0000000000000246 R12: 00007f51072cf6c8
[  +0.000001] R13: 0000000000000d68 R14: 00007f5106e15a00 R15: 0000000000000d68
[  +0.000002]  </TASK>
[  +0.000128] INFO: task (piserver):1607062 blocked for more than 120 seconds.
[  +0.000001]       Tainted: G S      W          6.4.0+ #39
[  +0.000001] "echo 0 > /proc/sys/kernel/hung_task_timeout_secs" disables this message.
[  +0.000000] task:(piserver)      state:D stack:0     pid:1607062 ppid:1      flags:0x00000002
[  +0.000002] Call Trace:
[  +0.000001]  <TASK>
[  +0.000001]  __schedule+0x3d5/0x15f0
[  +0.000002]  ? __kmem_cache_alloc_node+0x1b1/0x320
[  +0.000003]  schedule+0x68/0x110
[  +0.000003]  schedule_preempt_disabled+0x15/0x30
[  +0.000002]  __mutex_lock.constprop.0+0x3d8/0x770
[  +0.000002]  __mutex_lock_slowpath+0x13/0x20
[  +0.000001]  mutex_lock+0x3e/0x50
[  +0.000002]  cgroup_kn_lock_live+0x47/0xf0
[  +0.000002]  __cgroup_procs_write+0x3e/0x180
[  +0.000002]  cgroup_procs_write+0x17/0x30
[  +0.000002]  cgroup_file_write+0x8c/0x190
[  +0.000001]  ? __check_object_size+0x2a3/0x310
[  +0.000003]  kernfs_fop_write_iter+0x153/0x1e0
[  +0.000002]  vfs_write+0x2cf/0x400
[  +0.000003]  ksys_write+0x67/0xf0
[  +0.000002]  __x64_sys_write+0x19/0x30
[  +0.000001]  do_syscall_64+0x59/0x90
[  +0.000002]  ? exit_to_user_mode_prepare+0x39/0x190
[  +0.000003]  ? irqentry_exit_to_user_mode+0x9/0x20
[  +0.000002]  ? irqentry_exit+0x43/0x50
[  +0.000001]  ? exc_page_fault+0x95/0x1b0
[  +0.000001]  entry_SYSCALL_64_after_hwframe+0x6e/0xd8
[  +0.000002] RIP: 0033:0x7f9a68314a6f
[  +0.000000] RSP: 002b:00007fffd0e51fd0 EFLAGS: 00000293 ORIG_RAX: 0000000000000001
[  +0.000002] RAX: ffffffffffffffda RBX: 0000000000000008 RCX: 00007f9a68314a6f
[  +0.000000] RDX: 0000000000000008 RSI: 00007fffd0e5218a RDI: 0000000000000003
[  +0.000001] RBP: 00007fffd0e5218a R08: 0000000000000000 R09: 00007fffd0e52010
[  +0.000001] R10: 0000000000000000 R11: 0000000000000293 R12: 0000000000000008
[  +0.000001] R13: 00005644ec569cb0 R14: 00007f9a68415a00 R15: 0000000000000008
[  +0.000001]  </TASK>
[  +6.996450] audit: type=1400 audit(1690245873.626:157): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1619065/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[  +7.175238] audit: type=1400 audit(1690245880.798:158): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1619108/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[  +2.931534] audit: type=1400 audit(1690245883.730:159): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1619127/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.105076] audit: type=1400 audit(1690245893.838:160): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1619155/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[Jul25 00:45] audit: type=1400 audit(1690245903.942:161): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1619200/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.106562] audit: type=1400 audit(1690245914.050:162): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1619272/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[  +3.439124] rcu: INFO: rcu_preempt detected stalls on CPUs/tasks:
[  +0.000003] rcu:      Tasks blocked on level-1 rcu_node (CPUs 0-15): P1010/5:b..l
[  +0.000009] rcu:      (detected by 11, t=60007 jiffies, g=122497, q=1502891 ncpus=96)
[  +0.000006] task:kworker/u193:11 state:I stack:0     pid:1010  ppid:2      flags:0x00004000
[  +0.000004] Workqueue:  0x0 (events_power_efficient)
[  +0.000005] Call Trace:
[  +0.000002]  <TASK>
[  +0.000002]  __schedule+0x3d5/0x15f0
[  +0.000006]  ? add_timer+0x20/0x40
[  +0.000005]  ? queue_delayed_work_on+0x6e/0x80
[  +0.000004]  ? _raw_write_unlock_bh+0x1a/0x30
[  +0.000003]  schedule+0x68/0x110
[  +0.000003]  worker_thread+0xbd/0x3f0
[  +0.000002]  ? __pfx_worker_thread+0x10/0x10
[  +0.000002]  kthread+0xf4/0x130
[  +0.000004]  ? __pfx_kthread+0x10/0x10
[  +0.000002]  ret_from_fork+0x29/0x50
[  +0.000006]  </TASK>
[  +6.666093] audit: type=1400 audit(1690245924.154:163): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1619338/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.107491] audit: type=1400 audit(1690245934.262:164): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1619459/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.106095] audit: type=1400 audit(1690245944.366:165): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1619506/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[ +10.107349] audit: type=1400 audit(1690245954.474:166): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1619537/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
[Jul25 00:46] audit: type=1400 audit(1690245964.582:167): apparmor="ALLOWED" operation="open" class="file" profile="/usr/sbin/sssd" name="/proc/1619565/cmdline" pid=1942 comm="sssd_nss" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
```
The syndrome above is first get rcu read-side critical section been violated cuased by following code. Then jiffies will be wrong and core dump process caused by increasing jiffies and died because of VM_FAULT_OOM leaked out to the #PF handler. Retrying PF.

```c
bool bede_flush_node_rss(struct mem_cgroup *memcg) { // work around for every time call policy_node for delayed
	int nid;
	if (mem_cgroup_disabled()){
		return false;
	}
	mem_cgroup_flush_stats();
	for_each_node_state(nid, N_MEMORY) {
		u64 size;
		struct lruvec *lruvec;
		pg_data_t *pgdat = NODE_DATA(nid);
		if (!pgdat)
			return false;
		lruvec = mem_cgroup_lruvec(memcg, pgdat);
		if (!lruvec)
			return false;
		size = lruvec_page_state_local(lruvec, NR_ANON_MAPPED) >> PAGE_SHIFT;
		memcg->node_rss[nid] = size >> 20;
	}
	return true;
}
...
int policy_node(gfp_t gfp, struct mempolicy *policy, int nd)
{
        if (policy->mode != MPOL_BIND && bede_should_policy) {
        	struct mem_cgroup *memcg = get_mem_cgroup_from_mm(current->mm);
                if (memcg && root_mem_cgroup && memcg != root_mem_cgroup) {
                    if (bede_flush_node_rss(memcg)) {
                        // bede_append_page_walk_and_migration(current->cgroups->dfl_cgrp->bede);
                        nd = bede_get_node(memcg, nd);
                        return nd;
                    }
                }
        }
```

I tried [https://lwn.net/Articles/916583/](https://lwn.net/Articles/916583/) and [https://lwn.net/Articles/916583/](https://lwn.net/Articles/916583/). And I thought the race is possibly interrupt that caused into `__mod_node_page_state`, or memcg may encounter TOUTOC bug. I decided not to put un-preemptable job into hot path.

## General Debug process of segfaults.
Get the crash reason for (segfaults)[https://utcc.utoronto.ca/~cks/space/blog/linux/KernelSegfaultMessageMeaning] in dmesg, the dumped ip (without running gdb since gdb will trap all signal) will help you locate where's specific code section loaded to. you can know the line with addr2line or find the label in kcallsym with offset to see the assembly and map back to the source code.