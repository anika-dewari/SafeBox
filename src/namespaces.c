// File: src/namespaces.c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <sched.h>
#include <unistd.h>
#include <sys/mount.h>
#include <sys/types.h>
#include "safebox.h"
#include <signal.h>
// Set a size for the child's stack (1 MB)
#define STACK_SIZE (1024 * 1024)
static char child_stack[STACK_SIZE];

// Function to remap UID/GID within the User Namespace
int setup_userns_map(pid_t child_pid) {
    // NOTE: This must be executed by the PARENT process after clone()
    
    // Map UID: Maps the current effective UID of the PARENT to UID 0 (root) inside the CHILD
    char uid_map_path[256];
    sprintf(uid_map_path, "/proc/%d/uid_map", child_pid);
    
    FILE *uid_map_file = fopen(uid_map_path, "w");
    if (!uid_map_file) {
        perror("Failed to open uid_map");
        return -1;
    }
    // Format: 'container_id host_id range' -> Map container UID 0 to parent's UID 
    fprintf(uid_map_file, "0 %d 1\n", geteuid()); 
    fclose(uid_map_file);
    
    // Map GID: Similar process for GID
    char setgroups_path[256];
    sprintf(setgroups_path, "/proc/%d/setgroups", child_pid);
    FILE *setgroups_file = fopen(setgroups_path, "w");
    if (setgroups_file) {
        // Must disable setgroups check before writing gid_map
        fprintf(setgroups_file, "deny\n"); 
        fclose(setgroups_file);
    }
    
    char gid_map_path[256];
    sprintf(gid_map_path, "/proc/%d/gid_map", child_pid);
    FILE *gid_map_file = fopen(gid_map_path, "w");
    if (!gid_map_file) {
        perror("Failed to open gid_map");
        return -1;
    }
    // Format: 'container_id host_id range'
    fprintf(gid_map_file, "0 %d 1\n", getegid());
    fclose(gid_map_file);

    return 0;
}

// Function that the child process executes (your sandbox environment)
int sandbox_main(void *arg) {
    printf("[Sandbox] PID: %d (Inside namespace)\n", getpid());

    // 1. Filesystem Isolation (CLONE_NEWNS setup)
    // Make sure no mount changes in the sandbox affect the host
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) == -1) {
        perror("mount MS_PRIVATE failed");
        _exit(EXIT_FAILURE);
    }
    
    // Mount a minimal, clean /proc inside the new PID namespace
    if (mount("proc", "/proc", "proc", 0, NULL) != 0) {
        perror("mount /proc failed");
        _exit(EXIT_FAILURE);
    }
	// Mount /bin (or the directory containing /bin/sh)
    if (mount("/bin", "/bin", "none", MS_BIND | MS_REC, NULL) != 0) {
        perror("mount /bin failed"); _exit(EXIT_FAILURE);
    }
    
    // Mount /usr/bin 
    if (mount("/usr/bin", "/usr/bin", "none", MS_BIND | MS_REC, NULL) != 0) {
        perror("mount /usr/bin failed"); _exit(EXIT_FAILURE);
    }
    
    // Mount /lib (Essential for glibc/dynamic linker)
    if (mount("/lib", "/lib", "none", MS_BIND | MS_REC, NULL) != 0) {
        perror("mount /lib failed"); _exit(EXIT_FAILURE);
    printf("[Sandbox] New /proc mounted. Isolation established.\n");
   }

     if (apply_seccomp_filter() != 0) {
        fprintf(stderr, "[Sandbox] Fatal: Failed to apply Seccomp policy.\n");
        _exit(EXIT_FAILURE);
    }
     if (attach_to_cgroup(getpid()) != 0) {
        fprintf(stderr, "[Sandbox] Warning: Failed to attach to cgroup. Resource limits may not apply.\n");
        // needs review with Ayush
    }
    // Execute a process (e.g., a simple shell)
    char *const argv[] = { "/bin/sh", NULL };
    char *const envp[] = { "PATH=/bin:/usr/bin", NULL };
    
    printf("[Sandbox] Launching shell...\n");
    if (execve(argv[0], argv, envp) == -1) {
        perror("execve failed");
        _exit(EXIT_FAILURE);
    }
    
    return 0;
}

// Export the main cloning function for use in main.c
pid_t create_sandbox(void) {
    // Define all required namespace flags
    int namespace_flags = 
        CLONE_NEWPID |      // PID isolation
        CLONE_NEWNS |       // Mount isolation
        CLONE_NEWUTS |      // Hostname isolation
        CLONE_NEWIPC |      // IPC isolation
        CLONE_NEWUSER |     // User isolation (CRITICAL)
        CLONE_NEWNET;       // Network isolation
        
    // Use clone() to create the child in new namespaces
    pid_t child_pid = clone(
        sandbox_main, 
        child_stack + STACK_SIZE, // Top of stack
        namespace_flags | SIGCHLD, 
        NULL // No arguments passed to sandbox_main
    );

    if (child_pid == -1) {
        perror("clone failed");
        return -1;
    }
    
    // CRITICAL: Setup User Namespace mapping from parent process
    if (setup_userns_map(child_pid) == -1) {
        return -1;
    }

    return child_pid;
}
