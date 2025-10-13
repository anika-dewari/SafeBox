#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>

// --- Configuration ---
// This path must match the cgroup path created by Ayush's resource manager
#define CGROUP_BASE_PATH "/sys/fs/cgroup/cpu/SafeBox_Tasks/tasks" 
// If using cgroups V2, the path will be different: /sys/fs/cgroup/SafeBox_Tasks/cgroup.procs

int attach_to_cgroup(pid_t pid) {
    // 1. Construct the path to the 'tasks' file (or 'cgroup.procs' for V2)
    char tasks_path[256];
    
    // NOTE: For simplicity, we use a single path. In a real system, you'd check V1 vs V2
    // If Ayush is managing V1 CPU cgroups under /sys/fs/cgroup/cpu/
    snprintf(tasks_path, sizeof(tasks_path), "/sys/fs/cgroup/cpu/SafeBox_Tasks/tasks"); 
    
    // 2. Open the cgroup 'tasks' file for writing
    FILE *cgroup_file = fopen(tasks_path, "w");
    if (!cgroup_file) {
        // common point of failure: the cgroup folder 'SafeBox_Tasks' 
        // must be created and configured by Ayush's code *before* you call this function.
        perror("Failed to open cgroup tasks file (check Ayush's setup)");
        return -1;
    }

    // 3. Write the PID into the file to attach the process to the cgroup
    fprintf(cgroup_file, "%d", pid);
    
    // 4. Close and verify
    if (fclose(cgroup_file) == EOF) {
        perror("Failed to close cgroup tasks file");
        return -1;
    }

    printf("[Host] Attached sandbox PID %d to cgroup path: %s\n", pid, tasks_path);
    return 0;
}
