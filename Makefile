
CC = gcc
CFLAGS = -Wall -std=c99 -g
LDFLAGS = -lseccomp # Link against the libseccomp library
TARGET = build/safebox

# Source files
SRCS = src/main.c src/namespaces.c src/seccomp_policy.c src/cgroups_attach.c 

.PHONY: all clean install-deps integrated-demo demo-all test-integration help

all: $(TARGET)

$(TARGET): $(SRCS)
	@mkdir -p build
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

clean:
	rm -f $(TARGET)

# Install all Python dependencies
install-deps:
	@echo "Installing Python dependencies..."
	pip3 install -r backend/requirements.txt

# Run complete integrated demo (ALL THREE TEAM MEMBERS' WORK)
integrated-demo: install-deps
	@echo "=========================================="
	@echo "SafeBox - Integrated System Demo"
	@echo "Anika + Ayush + Ritika = ONE SYSTEM"
	@echo "=========================================="
	python3 integrated_demo.py complete

# Run all demo scenarios
demo-all: install-deps
	@echo "Running all integration scenarios..."
	python3 integrated_demo.py

# Quick demo of Banker's Algorithm only
demo-banker:
	python3 demo_banker_algorithm.py

# Test the integrated system
test-integration: install-deps
	@echo "Testing integrated system..."
	pytest tests/test_banker.py -v
	python3 integrated_demo.py 1
	python3 integrated_demo.py 2
	python3 integrated_demo.py 3

# Start integrated backend + web UI
start-integrated: install-deps
	@echo "Starting integrated backend..."
	@cd backend && PYTHONPATH=.. python3 -m uvicorn app.main:app --reload --port 8001 &
	@sleep 2
	@echo "Starting integrated web UI..."
	@python3 web/app.py &
	@echo "System running!"
	@echo "Backend: http://localhost:8001"
	@echo "Web UI: http://localhost:5001"

# Show help
help:
	@echo "SafeBox Integrated System - Makefile Commands"
	@echo "=============================================="
	@echo ""
	@echo "Integration Demos (Show All Three Working Together):"
	@echo "  make integrated-demo     - Complete integrated system demo"
	@echo "  make demo-all           - All scenarios interactively"
	@echo "  make start-integrated   - Start backend + web UI"
	@echo ""
	@echo "Individual Component Demos:"
	@echo "  make demo-banker        - Banker's Algorithm only"
	@echo ""
	@echo "Build & Test:"
	@echo "  make all               - Build C/C++ components"
	@echo "  make install-deps      - Install Python dependencies"
	@echo "  make test-integration  - Run integration tests"
	@echo "  make clean            - Clean build files"
	@echo ""
	@echo "Team Member Contributions:"
	@echo "  RITIKA: Banker Algorithm, Resource Management"
	@echo "  AYUSH:  cgroups, Monitoring, Performance"
	@echo "  ANIKA:  Security, Namespaces, seccomp"
