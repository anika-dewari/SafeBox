// File: src/main.c
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>

// Forward declarations from your other files
#include "safebox.h"

// --- Main Program ---
int main(int argc, char *argv[]) {
    printf("--- SafeBox Core Controller (Anika) ---\n");
    printf("[Host] Host PID: %d\n", getpid());
    
    // 1. Create the Isolated Sandbox Process
    pid_t child_pid = create_sandbox();
    
    if (child_pid == -1) {
        fprintf(stderr, "[Host] Failed to launch sandbox. Exiting.\n");
        return EXIT_FAILURE;
    }
    
    printf("[Host] Sandbox launched with Host PID: %d. Waiting...\n", child_pid);

    // 2. Wait for the child process to exit
    // This is where the Host controller monitors the sandbox
    int status;
    if (waitpid(child_pid, &status, 0) == -1) {
        perror("[Host] waitpid failed");
    }

    if (WIFEXITED(status)) {
        printf("[Host] Sandbox exited normally with status %d.\n", WEXITSTATUS(status));
    } else if (WIFSIGNALED(status)) {
        printf("[Host] Sandbox terminated by signal %d (Security Violation/Crash).\n", WTERMSIG(status));
    }

    printf("--- SafeBox Execution Finished ---\n");
    return EXIT_SUCCESS;
}
