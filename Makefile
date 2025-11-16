CC = gcc
CXX = g++
CFLAGS = -Wall -std=c99 -g
CXXFLAGS = -std=c++17 -g
LDFLAGS = -lseccomp
CMAKE = cmake

# Build directories
BUILD_DIR = build
SRC_DIR = src
CGROUP_DIR = cgroup_agent

# Targets
SAFEBOX_BIN = $(SRC_DIR)/safebox
CALC_BIN = $(SRC_DIR)/calc_with_selftest
TEST_BIN = $(SRC_DIR)/test
CGROUP_BIN = $(BUILD_DIR)/safebox_cgroup

.PHONY: all clean install-deps real-system help build-c build-cpp

all: build-c build-cpp

.PHONY: all clean install-deps real-system help build-c build-cpp

all: build-c build-cpp

# Build C binaries (SafeBox sandbox and test apps)
build-c:
	@echo "🔨 Building C components..."
	@cd $(SRC_DIR) && $(CC) $(CFLAGS) safebox.c -o safebox $(LDFLAGS)
	@cd $(SRC_DIR) && $(CC) $(CFLAGS) calc_with_selftest.c -o calc_with_selftest
	@cd $(SRC_DIR) && $(CC) $(CFLAGS) test.c -o test
	@echo "✅ C binaries built: safebox, calc_with_selftest, test"

# Build C++ cgroup agent
build-cpp:
	@echo "🔨 Building C++ cgroup agent..."
	@mkdir -p $(BUILD_DIR)
	@cd $(BUILD_DIR) && $(CMAKE) ../$(CGROUP_DIR) && $(MAKE)
	@echo "✅ C++ cgroup agent built: $(CGROUP_BIN)"

# Build everything for real system
real-system: all
	@echo ""
	@echo "✅ Real System Components Ready!"
	@echo "   - SafeBox Sandbox: $(SAFEBOX_BIN)"
	@echo "   - cgroup Agent: $(CGROUP_BIN)"
	@echo "   - Test Apps: calc_with_selftest, test"
	@echo ""
	@echo "🚀 Run with: sudo python3 cli/real_safebox_cli.py"

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
	@echo "╔═══════════════════════════════════════════════════════════╗"
	@echo "║          SafeBox Real System - Build Commands            ║"
	@echo "╚═══════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🏗️  Build Commands:"
	@echo "  make all              - Build all components (C + C++)"
	@echo "  make build-c          - Build SafeBox sandbox + test apps"
	@echo "  make build-cpp        - Build cgroup agent"
	@echo "  make real-system      - Build everything for real execution"
	@echo ""
	@echo "🚀 Run Real System:"
	@echo "  make install-deps     - Install Python dependencies"
	@echo "  sudo python3 cli/real_safebox_cli.py"
	@echo ""
	@echo "🧪 Legacy Demos:"
	@echo "  make integrated-demo  - Complete integrated system demo"
	@echo "  make demo-all         - All scenarios interactively"
	@echo "  make demo-banker      - Banker's Algorithm only"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean           - Clean build files"
	@echo ""
	@echo "📊 System Flow:"
	@echo "  User Request → Banker's Algorithm → cgroups → SafeBox → App"
	@echo ""
	@echo "👥 Team: Ritika (Banker) + Ayush (cgroups) + Anika (Sandbox)"
