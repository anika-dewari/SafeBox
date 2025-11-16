/*
 * memory_intensive.c - Memory-bound workload
 * Allocates and uses memory intensively
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define MB (1024 * 1024)

int main(int argc, char *argv[]) {
    int mem_mb = 50; // default 50MB
    int duration = 5; // default 5 seconds
    
    if (argc > 1) {
        mem_mb = atoi(argv[1]);
        if (mem_mb <= 0) mem_mb = 50;
    }
    if (argc > 2) {
        duration = atoi(argv[2]);
        if (duration <= 0) duration = 5;
    }
    
    printf("Memory Intensive Job Started\n");
    printf("Allocating %dMB for %d seconds\n", mem_mb, duration);
    fflush(stdout);
    
    // Allocate memory
    char *buffer = (char*)malloc(mem_mb * MB);
    if (!buffer) {
        fprintf(stderr, "Failed to allocate %dMB\n", mem_mb);
        return 1;
    }
    
    // Touch all pages to ensure allocation
    printf("Touching memory pages...\n");
    fflush(stdout);
    for (int i = 0; i < mem_mb; i++) {
        memset(buffer + (i * MB), i % 256, MB);
    }
    
    printf("Memory allocated and initialized\n");
    printf("Holding memory for %d seconds...\n", duration);
    fflush(stdout);
    
    sleep(duration);
    
    // Verify some data
    unsigned long checksum = 0;
    for (int i = 0; i < mem_mb * MB; i += 4096) {
        checksum += buffer[i];
    }
    
    printf("Checksum: %lu\n", checksum);
    printf("Memory Intensive Job Completed!\n");
    fflush(stdout);
    
    free(buffer);
    return 0;
}
