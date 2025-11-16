/*
 * quick_job.c - Fast completing job
 * Useful for testing rapid job submission/completion
 */

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    int count = 100;
    
    if (argc > 1) {
        count = atoi(argv[1]);
        if (count <= 0) count = 100;
    }
    
    printf("Quick Job Started\n");
    printf("Processing %d items...\n", count);
    fflush(stdout);
    
    int sum = 0;
    for (int i = 1; i <= count; i++) {
        sum += i;
    }
    
    printf("Sum of 1 to %d = %d\n", count, sum);
    printf("Quick Job Completed!\n");
    fflush(stdout);
    
    return 0;
}
