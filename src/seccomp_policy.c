// File: src/seccomp_policy.c
#include <stdio.h>
#include <stdlib.h>
#include <seccomp.h>
#include <linux/audit.h>
#include <sys/syscall.h>
#include <errno.h>
// This function loads and enforces the Seccomp filter
int apply_seccomp_filter() {
    scmp_filter_ctx ctx;
    
    // 1. Initialize the filter with the default action: KILL (terminate the process)
    // This implements the principle of least privilege: deny all, then allow specific.
    ctx = seccomp_init(SCMP_ACT_KILL); 
    if (!ctx) {
        perror("seccomp_init failed");
        return -1;
    }

    // 2. Allow essential system calls (Whitelist)
    // Necessary for any process to run, read/write, and exit.
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(clone3), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(rt_sigreturn), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(openat), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(close), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(execve), 0); // To execute the shell
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(brk), 0); // For dynamic memory allocation
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(mmap), 0); // For memory mapping
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(munmap), 0);  // Unmapping memory
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(mprotect), 0);// Setting memory permissions (e.g., for executable code)
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(arch_prctl), 0);
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(set_tid_address), 0);
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(rseq), 0); 
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(futex), 0);   
// --- PROCESS/SIGNAL MANAGEMENT (CRUCIAL FOR CLEAN STARTUP/SIGNALS) ---
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(rt_sigaction), 0); // Setting signal handlers
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(rt_sigprocmask), 0); // Manipulating signal mask

// --- PROCESS STATUS / INFO ---
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(fstat), 0); // Getting file status (needed by linker)
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(ioctl), 0);

    // SCMP_ACT_ERRNO: Block reboot but return "Operation not permitted"
    if (seccomp_rule_add(ctx, SCMP_ACT_ERRNO(EPERM), SCMP_SYS(reboot), 0) != 0) {
        perror("Failed to add reboot rule");
    }

    // SCMP_ACT_LOG: Allow a benign but monitored call, logging the attempt (e.g., uname)
    if (seccomp_rule_add(ctx, SCMP_ACT_LOG, SCMP_SYS(uname), 0) != 0) {
        perror("Failed to add uname rule");
    }
    
    // SCMP_ACT_TRAP: Trap the process for inspection if it tries to mount
    if (seccomp_rule_add(ctx, SCMP_ACT_TRAP, SCMP_SYS(mount), 0) != 0) {
        perror("Failed to add mount rule");
    }

    // 4. Load the filter into the kernel (makes it immutable)
    if (seccomp_load(ctx) != 0) {
        perror("seccomp_load failed");
        seccomp_release(ctx);
        return -1;
    }

    seccomp_release(ctx);
    printf("[Sandbox] Seccomp BPF filter applied.\n");
    return 0;
}
