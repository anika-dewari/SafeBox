/*
 * io_intensive.c - I/O-bound workload
 * Performs file operations repeatedly
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

int main(int argc, char *argv[]) {
    int duration = 5; // default 5 seconds
    
    if (argc > 1) {
        duration = atoi(argv[1]);
        if (duration <= 0) duration = 5;
    }
    
    printf("I/O Intensive Job Started\n");
    printf("Will perform file operations for %d seconds\n", duration);
    fflush(stdout);
    
    char filename[] = "/tmp/safebox_io_test.tmp";
    time_t start = time(NULL);
    int iterations = 0;
    
    while (time(NULL) - start < duration) {
        // Write data
        FILE *f = fopen(filename, "w");
        if (f) {
            for (int i = 0; i < 1000; i++) {
                fprintf(f, "Line %d: This is test data for I/O operations\n", i);
            }
            fclose(f);
        }
        
        // Read data
        f = fopen(filename, "r");
        if (f) {
            char buffer[256];
            while (fgets(buffer, sizeof(buffer), f)) {
                // Just read and discard
            }
            fclose(f);
        }
        
        iterations++;
    }
    
    // Cleanup
    remove(filename);
    
    printf("Completed %d I/O cycles\n", iterations);
    printf("I/O Intensive Job Completed!\n");
    fflush(stdout);
    
    return 0;
}
