/* safebox.c
 *
 * Minimal sandbox prototype:
 *  - clone() with PID, UTS, mount namespaces
 *  - mount a private /proc in the child
 *  - detect cgroup v2 vs v1 and attempt to add child to a memory-limited cgroup
 *  - apply a reasonable libseccomp whitelist
 *  - drop privileges to nobody:nogroup and optionally chroot (disabled by default)
 *
 * Notes:
 *  - Run as root (or with necessary capabilities) for namespace/cgroup operations.
 *  - On WSL2 you may need to remove cgroup use (this code will just warn/continue).
 *  - This is an educational prototype — do not consider it production-grade sandboxing.
 *
 * Compile:
 *   gcc -O2 safebox.c -o safebox -lseccomp
 *
 * Example run:
 *   sudo ./safebox /bin/sh
 */

#define _GNU_SOURCE
#include <sched.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/prctl.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <seccomp.h>
#include <pwd.h>
#include <grp.h>
#include <sys/syscall.h>
#include <stdint.h>

#define STACK_SIZE (1024 * 1024)
static char child_stack[STACK_SIZE];

static const char *CGROUP_V1_BASE = "/sys/fs/cgroup/memory"; //Inside this directory, each sandbox (or application) can create its own sub-folder to control memory usage.
static const char *CGROUP_NAME = "safebox"; //When the sandbox starts, it creates a cgroup with this name.

/* write a string to a file path, return 0 on success */
static int write_file(const char *path, const char *content) {
    int fd = open(path, O_WRONLY | O_CLOEXEC); //open in write only and automatically closes the files on execute command
    if (fd < 0) return -1;
    ssize_t w = write(fd, content, strlen(content));
    close(fd);
    return (w == (ssize_t)strlen(content)) ? 0 : -1;
}

/* detect cgroup v2 by checking /sys/fs/cgroup/cgroup.controllers */
static int is_cgroup_v2(void) {
    return access("/sys/fs/cgroup/cgroup.controllers", F_OK) == 0;
}

/* Setup a cgroup for a pid with memory limit; handles v2 and v1 best-effort.
 * memory_limit_bytes==0 => don't set a limit, only try to add to group.
 * Returns 0 on success, -1 on failure (but caller will continue).
 */
static int setup_cgroup_for_pid(pid_t pid, size_t memory_limit_bytes) {
    char path[512];
    char tmp[64];
    int ret = -1;

    if (is_cgroup_v2()) {
        // cgroup v2 unified hierarchy
        snprintf(path, sizeof(path), "/sys/fs/cgroup/%s", CGROUP_NAME); //create cgroup directory
        if (mkdir(path, 0755) < 0 && errno != EEXIST) {
            perror("mkdir(cgroup v2)");
            return -1;
        }
        if (memory_limit_bytes > 0) { //set memory limit
            char mempath[512];
            snprintf(mempath, sizeof(mempath), "%s/memory.max", path);
            snprintf(tmp, sizeof(tmp), "%zu", memory_limit_bytes);
            if (write_file(mempath, tmp) != 0) {
                perror("write memory.max (v2)");
                // continue
            }
        }
        // add pid
        char procs[512];
        snprintf(procs, sizeof(procs), "%s/cgroup.procs", path);
        snprintf(tmp, sizeof(tmp), "%d", pid);
        if (write_file(procs, tmp) != 0) {
            perror("write cgroup.procs (v2)");
            return -1;
        }
        ret = 0;
    } else {
        // try cgroup v1 memory controller path
        if (access(CGROUP_V1_BASE, F_OK) != 0) {
            fprintf(stderr, "Memory cgroup mount not found at %s. Is cgroup v1 memory enabled?\n", CGROUP_V1_BASE);
            return -1;
        }
        snprintf(path, sizeof(path), "%s/%s", CGROUP_V1_BASE, CGROUP_NAME);
        if (mkdir(path, 0755) < 0 && errno != EEXIST) {
            perror("mkdir(cgroup v1)");
            return -1;
        }
        if (memory_limit_bytes > 0) {
            char limit_path[512];
            snprintf(limit_path, sizeof(limit_path), "%s/memory.limit_in_bytes", path);
            snprintf(tmp, sizeof(tmp), "%zu", memory_limit_bytes);
            if (write_file(limit_path, tmp) != 0) {
                perror("write memory.limit_in_bytes (v1)");
                // continue
            }
        }
        char procs_path[512];
        snprintf(procs_path, sizeof(procs_path), "%s/cgroup.procs", path);
        snprintf(tmp, sizeof(tmp), "%d", pid);
        if (write_file(procs_path, tmp) != 0) {
            perror("write cgroup.procs (v1)");
            return -1;
        }
        ret = 0;
    }

    return ret;
}

/* Apply a permissive-but-sane seccomp whitelist using libseccomp.
 * Default action is KILL on violation.
 */
#ifndef SCMP_SYS_newfstatat
#define SCMP_SYS_newfstatat SCMP_SYS(fstatat)
#endif

static int apply_basic_seccomp_policy(void) {
    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL);
    if (!ctx) {
        fprintf(stderr, "seccomp_init failed\n");
        return -1;
    }

    int allow_list[] = {
        /* io / process control */
        SCMP_SYS(read), SCMP_SYS(write), SCMP_SYS(exit), SCMP_SYS(exit_group),
        SCMP_SYS(close), SCMP_SYS(readlink), SCMP_SYS(lseek), SCMP_SYS(readlinkat),
        SCMP_SYS(pread64), SCMP_SYS(pwrite64), SCMP_SYS(writev), SCMP_SYS(readv),

        /* memory / brk / mmap */
        SCMP_SYS(brk), SCMP_SYS(mmap), SCMP_SYS(munmap), SCMP_SYS(mremap), SCMP_SYS(mprotect),
        SCMP_SYS(madvise), SCMP_SYS(msync), SCMP_SYS(mincore),

        /* file ops */
        SCMP_SYS(open), SCMP_SYS(openat), SCMP_SYS(fstat), SCMP_SYS(stat), SCMP_SYS(lstat),
        SCMP_SYS(newfstatat), SCMP_SYS(access), SCMP_SYS(faccessat), SCMP_SYS(faccessat2),
        SCMP_SYS(getdents), SCMP_SYS(getdents64), SCMP_SYS(getcwd), SCMP_SYS(statx), 
        SCMP_SYS(fcntl), SCMP_SYS(fstatfs), SCMP_SYS(statfs), SCMP_SYS(truncate), 
        SCMP_SYS(ftruncate), SCMP_SYS(rename), SCMP_SYS(renameat), SCMP_SYS(renameat2),
        SCMP_SYS(unlink), SCMP_SYS(unlinkat), SCMP_SYS(mkdir), SCMP_SYS(mkdirat),
        SCMP_SYS(rmdir), SCMP_SYS(link), SCMP_SYS(linkat), SCMP_SYS(symlink), 
        SCMP_SYS(symlinkat), SCMP_SYS(chmod), SCMP_SYS(fchmod), SCMP_SYS(fchmodat),

        /* signals */
        SCMP_SYS(rt_sigaction), SCMP_SYS(rt_sigprocmask), SCMP_SYS(rt_sigreturn),
        SCMP_SYS(sigaltstack), SCMP_SYS(sigreturn), SCMP_SYS(rt_sigsuspend),
        SCMP_SYS(kill), SCMP_SYS(tkill), SCMP_SYS(tgkill),

        /* time / random */
        SCMP_SYS(clock_gettime), SCMP_SYS(clock_nanosleep), SCMP_SYS(nanosleep), 
        SCMP_SYS(gettimeofday), SCMP_SYS(getrandom), SCMP_SYS(time),

        /* threads / futexes */
        SCMP_SYS(futex), SCMP_SYS(set_robust_list), SCMP_SYS(set_tid_address),
        SCMP_SYS(get_robust_list), SCMP_SYS(rseq),

        /* process lifecycle */
        SCMP_SYS(clone), SCMP_SYS(clone3), SCMP_SYS(execve), SCMP_SYS(execveat), 
        SCMP_SYS(wait4), SCMP_SYS(waitid), SCMP_SYS(getpid), SCMP_SYS(vfork), SCMP_SYS(fork),

        /* uid/gid and prctl */
        SCMP_SYS(getuid), SCMP_SYS(geteuid), SCMP_SYS(getppid), SCMP_SYS(getgid), SCMP_SYS(getegid),
        SCMP_SYS(getgroups), SCMP_SYS(prctl), SCMP_SYS(arch_prctl), SCMP_SYS(capget), SCMP_SYS(capset),
        SCMP_SYS(setuid), SCMP_SYS(setgid), SCMP_SYS(setgroups),
        SCMP_SYS(setreuid), SCMP_SYS(setregid), SCMP_SYS(setresuid), SCMP_SYS(setresgid),

        /* resource limits */
        SCMP_SYS(getrlimit), SCMP_SYS(setrlimit), SCMP_SYS(prlimit64), SCMP_SYS(getrusage),

        /* sockets basics (for shells that might use network tools) */
        SCMP_SYS(socket), SCMP_SYS(connect), SCMP_SYS(bind), SCMP_SYS(listen),
        SCMP_SYS(accept), SCMP_SYS(accept4), SCMP_SYS(sendto), SCMP_SYS(recvfrom),
        SCMP_SYS(sendmsg), SCMP_SYS(recvmsg), SCMP_SYS(socketpair), SCMP_SYS(getsockname),
        SCMP_SYS(getpeername), SCMP_SYS(getsockopt), SCMP_SYS(setsockopt),
        SCMP_SYS(shutdown),

        /* epoll/poll/select */
        SCMP_SYS(poll), SCMP_SYS(ppoll), SCMP_SYS(select), SCMP_SYS(pselect6),
        SCMP_SYS(epoll_create), SCMP_SYS(epoll_create1),
        SCMP_SYS(epoll_ctl), SCMP_SYS(epoll_wait), SCMP_SYS(epoll_pwait),

        /* pipes */
        SCMP_SYS(pipe), SCMP_SYS(pipe2),

        /* misc */
        SCMP_SYS(ioctl), SCMP_SYS(dup), SCMP_SYS(dup2), SCMP_SYS(dup3), 
        SCMP_SYS(chdir), SCMP_SYS(fchdir),
        SCMP_SYS(uname), SCMP_SYS(setpgid), SCMP_SYS(getpgid), SCMP_SYS(getsid), SCMP_SYS(setsid),
        SCMP_SYS(getpriority), SCMP_SYS(setpriority),
        SCMP_SYS(sysinfo), SCMP_SYS(umask), SCMP_SYS(getpgrp),
        SCMP_SYS(eventfd), SCMP_SYS(eventfd2), SCMP_SYS(signalfd), SCMP_SYS(signalfd4),
        SCMP_SYS(timerfd_create), SCMP_SYS(timerfd_settime), SCMP_SYS(timerfd_gettime),
       SCMP_SYS(gettid),
SCMP_SYS(futex_waitv),
SCMP_SYS(getcpu),
SCMP_SYS(prlimit64),
SCMP_SYS(sched_getaffinity),
SCMP_SYS(sched_yield),
SCMP_SYS(set_robust_list),
SCMP_SYS(set_tid_address),
SCMP_SYS(sched_setparam),
SCMP_SYS(sched_getparam),
SCMP_SYS(sched_setscheduler),
SCMP_SYS(sched_getscheduler),
SCMP_SYS(sched_get_priority_max),
SCMP_SYS(sched_get_priority_min), 
        /* terminal control - critical for interactive shells */
        SCMP_SYS(ioctl)  /* already listed but emphasizing importance */
    };

    /* Add syscalls by number for architecture-specific ones that may not have names */
    int raw_syscalls[] = { 62, 111 };  /* ustat/lstat variants, getpgrp variants */
    for (size_t i = 0; i < sizeof(raw_syscalls)/sizeof(raw_syscalls[0]); ++i) {
        if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, raw_syscalls[i], 0) < 0) {
            /* May fail if syscall doesn't exist on this arch, continue */
        }
    }

    size_t n = sizeof(allow_list)/sizeof(allow_list[0]);
    for (size_t i = 0; i < n; ++i) {
        if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, allow_list[i], 0) < 0) {
            perror("seccomp_rule_add");
            seccomp_release(ctx);
            return -1;
        }
    }

    if (seccomp_load(ctx) < 0) {
        perror("seccomp_load");
        seccomp_release(ctx);
        return -1;
    }

    seccomp_release(ctx);
    return 0;
}

/* Drop privileges to nobody:nogroup and optionally chroot (pass NULL to skip chroot) */
static int drop_privileges_and_chroot(const char *new_root) {
    if (new_root) {
        if (chdir(new_root) != 0) { //Moves the current working directory into the directory that will become root.
            perror("chdir new_root");
            return -1;
        }
        if (chroot(new_root) != 0) { //Changes the process’s root directory (/) to new_root.
            perror("chroot");
            return -1;
        }
    }

    struct passwd *pw = getpwnam("nobody"); //Fetches UID/GID of the Linux user nobody.
    if (!pw) {
        fprintf(stderr, "user 'nobody' not found\n");
        return -1;
    }

    if (setgid(pw->pw_gid) != 0) {
        perror("setgid");
        return -1;
    }
    if (setuid(pw->pw_uid) != 0) {
        perror("setuid");
        return -1;
    }

    /* NO_NEW_PRIVS is now set earlier, before this function */

    return 0;
}

/* child code that runs inside new namespaces */
static int child_main(void *arg) {
    char **argv = (char **)arg;

    /* Make mounts private so changes inside don't escape */
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) != 0) {
        perror("mount MS_PRIVATE");
        // non-fatal
    }

    /* mount a new proc for the PID namespace */
    if (mkdir("/proc", 0555) < 0 && errno != EEXIST) {
        perror("mkdir /proc");
    }
    if (mount("proc", "/proc", "proc", MS_NOSUID | MS_NOEXEC | MS_NODEV, NULL) != 0) {
        perror("mount /proc");
        // non-fatal for demo
    }

    if (sethostname("safebox", strlen("safebox")) != 0) {
        // non-fatal
    }

    /* Prevent any new privileges before anything else */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        perror("prctl(NO_NEW_PRIVS) in child");
        // continue anyway
    }

    /* drop privileges BEFORE applying seccomp (no chroot by default here) */
    if (drop_privileges_and_chroot(NULL) != 0) {
        fprintf(stderr, "Warning: failed to drop privileges\n");
    }

    /* apply seccomp policy AFTER dropping privileges */
    if (apply_basic_seccomp_policy() != 0) {
        fprintf(stderr, "Warning: seccomp policy failed to load; continuing without seccomp\n");
        // Insecure fallback — for demo only
    }

    /* exec the requested program */
    execvp(argv[0], argv);
    perror("execvp");
    return 1;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <program> [args...]\n", argv[0]);
        return 1;
    }

    char **child_args = &argv[1];

    /* Use PID, UTS, and mount namespaces. Avoid CLONE_NEWNET for WSL compatibility. */
    int clone_flags = CLONE_NEWPID | CLONE_NEWUTS | CLONE_NEWNS | SIGCHLD;

    pid_t child = clone(child_main, child_stack + STACK_SIZE, clone_flags, child_args);
    if (child == -1) {
        perror("clone");
        return 1;
    }

    printf("Spawned sandbox child PID: %d\n", child);

    /* Try to set up a cgroup for the child (200 MB). If this fails, continue. */
    size_t mem_limit = 200 * 1024 * 1024;
    if (setup_cgroup_for_pid(child, mem_limit) != 0) {
        fprintf(stderr, "Warning: failed to setup cgroup for child (continuing)\n");
    } else {
        printf("Added child to cgroup '%s' with memory limit %zu bytes\n", CGROUP_NAME, mem_limit);
    }

    /* Wait for child */
    int status;
    if (waitpid(child, &status, 0) == -1) {
        perror("waitpid");
        return 1;
    }

    if (WIFEXITED(status)) {
        printf("Sandboxed process exited with code %d\n", WEXITSTATUS(status));
    } else if (WIFSIGNALED(status)) {
        printf("Sandboxed process killed by signal %d\n", WTERMSIG(status));
    } else {
        printf("Sandboxed process ended (status 0x%x)\n", status);
    }

    /* best-effort: cleanup cgroup v2/v1 directory (may fail if processes still inside) */
    if (is_cgroup_v2()) {
        char cgpath[256];
        snprintf(cgpath, sizeof(cgpath), "/sys/fs/cgroup/%s", CGROUP_NAME);
        rmdir(cgpath); // ignore errors
    } else {
        char cgpath[256];
        snprintf(cgpath, sizeof(cgpath), "%s/%s", CGROUP_V1_BASE, CGROUP_NAME);
        rmdir(cgpath);
    }

    return 0;
}
