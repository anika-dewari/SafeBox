/*
 * sleep_job.c - A simple program that sleeps for a specified duration
 * Used to demonstrate concurrent resource allocation in SafeBox
 *
 * Usage: ./sleep_job [seconds]
 * Example: ./sleep_job 10
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    int duration = 10; // default 10 seconds
    
    if (argc > 1) {
        duration = atoi(argv[1]);
        if (duration <= 0) {
            fprintf(stderr, "Invalid duration, using 10 seconds\n");
            duration = 10;
        }
    }
    
    printf("Job started - will sleep for %d seconds\n", duration);
    printf("Simulating work...\n");
    fflush(stdout);
    
    sleep(duration);
    
    printf("Job completed successfully!\n");
    fflush(stdout);
    
    return 0;
}
