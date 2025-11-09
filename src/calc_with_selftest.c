/*
 calc_with_selftest.c
 Simple calculator with explicit, labelled self-test modes for sandbox testing.

 Usage:
   Compile:
     gcc -O2 calc_with_selftest.c -o calc_with_selftest

   Run calculator:
     ./calc_with_selftest add 2 3
     ./calc_with_selftest mul 7 8

   Run self-tests (ONLY inside your sandbox):
     sudo ./safebox ./calc_with_selftest --selftest=crash
     sudo ./safebox ./calc_with_selftest --selftest=memhog

 WARNING:
   The selftest modes intentionally cause faults or heavy memory usage.
   Run them ONLY inside your SafeBox sandbox to demonstrate containment.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* Crash test: intentionally dereference NULL to trigger SIGSEGV */
static void run_crash_test(void) {
    printf("[SELFTEST] crash: about to dereference NULL (will SIGSEGV)\n");
    fflush(stdout);
    int *p = NULL;
    *p = 42; /* SIGSEGV */
    /* unreachable */
}

/* Memhog test: repeatedly allocate blocks until failure or kill */
static void run_memhog_test(void) {
    const size_t block = 10 * 1024 * 1024; /* 10 MiB */
    size_t i = 0;
    printf("[SELFTEST] memhog: allocating 10 MiB blocks until failure or kill\n");
    fflush(stdout);
    while (1) {
        void *p = malloc(block);
        if (!p) {
            fprintf(stderr, "[SELFTEST] malloc failed after %zu blocks (~%zu MiB)\n",
                    i, (i * block) / (1024*1024));
            break;
        }
        /* touch memory so pages are allocated */
        memset(p, 0xAA, block);
        ++i;
        if ((i & 0x7) == 0) { putchar('.'); fflush(stdout); }
        usleep(10000); /* small pause so output appears */
    }
    printf("\n[SELFTEST] memhog exiting\n");
}

/* Simple CLI calculator: add, sub, mul, div */
static int run_calculator(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Usage: %s <op> <a> <b>\nOperations: add sub mul div\n", argv[0]);
        return 1;
    }
    const char *op = argv[1];
    double a = atof(argv[2]);
    double b = atof(argv[3]);
    if (strcmp(op, "add") == 0) {
        printf("%g\n", a + b);
    } else if (strcmp(op, "sub") == 0) {
        printf("%g\n", a - b);
    } else if (strcmp(op, "mul") == 0) {
        printf("%g\n", a * b);
    } else if (strcmp(op, "div") == 0) {
        if (b == 0) { fprintf(stderr, "error: division by zero\n"); return 2; }
        printf("%g\n", a / b);
    } else {
        fprintf(stderr, "unknown op: %s\n", op);
        return 1;
    }
    return 0;
}

int main(int argc, char *argv[]) {
    /* If explicit selftest flag used, run the test */
    if (argc >= 2 && strncmp(argv[1], "--selftest=", 11) == 0) {
        const char *mode = argv[1] + 11;
        if (strcmp(mode, "crash") == 0) {
            run_crash_test();
            return 0; /* unreachable if crash happens */
        } else if (strcmp(mode, "memhog") == 0) {
            run_memhog_test();
            return 0;
        } else {
            fprintf(stderr, "Unknown selftest mode: %s\n", mode);
            return 1;
        }
    }

    /* Otherwise behave as calculator (accept op and two operands) */
    return run_calculator(argc, argv);
}
