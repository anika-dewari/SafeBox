// File: src/safebox.h

#ifndef SAFBOX_H
#define SAFBOX_H

#include <sys/types.h>

// --- Functions from src/namespaces.c ---
pid_t create_sandbox(void);

// --- Functions from src/seccomp_policy.c ---
int apply_seccomp_filter(void);

// --- Functions from src/cgroups_attach.c ---
int attach_to_cgroup(pid_t pid);

#endif // SAFBOX_H
