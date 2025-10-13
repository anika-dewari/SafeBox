
CC = gcc
CFLAGS = -Wall -std=c99 -g
LDFLAGS = -lseccomp # Link against the libseccomp library
TARGET = build/safebox

# Source files
SRCS = src/main.c src/namespaces.c src/seccomp_policy.c src/cgroups_attach.c 

all: $(TARGET)

$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

clean:
	rm -f $(TARGET)
