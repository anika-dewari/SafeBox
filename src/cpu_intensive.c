/*
 * cpu_intensive.c - CPU-bound workload
 * Performs intensive calculations to stress CPU
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

int main(int argc, char *argv[]) {
    int duration = 5; // default 5 seconds
    
    if (argc > 1) {
        duration = atoi(argv[1]);
        if (duration <= 0) duration = 5;
    }
    
    printf("CPU Intensive Job Started\n");
    printf("Will perform calculations for %d seconds\n", duration);
    fflush(stdout);
    
    time_t start = time(NULL);
    unsigned long long iterations = 0;
    double result = 0.0;
    
    // CPU-intensive calculations
    while (time(NULL) - start < duration) {
        for (int i = 0; i < 1000000; i++) {
            result += sqrt(i * 3.14159) * sin(i) * cos(i);
        }
        iterations++;
    }
    
    printf("Completed %llu million iterations\n", iterations);
    printf("Final result: %f\n", result);
    printf("CPU Intensive Job Completed!\n");
    fflush(stdout);
    
    return 0;
}
