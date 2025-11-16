# 🔒 SafeBox Real System - Quick Start Guide

## What Changed? Simulation → Real System

### Before (Simulation):
- ❌ Fake process management
- ❌ No actual resource limits
- ❌ Just algorithm demonstration

### Now (Real System):
- ✅ **Real Banker's Algorithm** safety checks
- ✅ **Real cgroups** for CPU and memory limits
- ✅ **Real SafeBox** sandbox with namespaces + seccomp
- ✅ **Real applications** executed safely

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Request                         │
│              (Application + Resources)                  │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│          Banker's Algorithm (Ritika)                    │
│    ┌────────────────────────────────────┐               │
│    │  Safety Check                      │               │
│    │  • Available resources             │               │
│    │  • Process needs                   │               │
│    │  • Safe sequence computation       │               │
│    └────────┬───────────────────────────┘               │
│             │                                            │
│         ✅ Safe?                                         │
│             │                                            │
└─────────────┼────────────────────────────────────────────┘
              │
          Yes │ No → REJECT
              ▼
┌─────────────────────────────────────────────────────────┐
│         cgroup Manager (Ayush)                          │
│    ┌────────────────────────────────────┐               │
│    │ 1. Create cgroup                   │               │
│    │ 2. Set CPU limit (%)               │               │
│    │ 3. Set Memory limit (MB)           │               │
│    └────────┬───────────────────────────┘               │
└─────────────┼────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│          SafeBox Sandbox (Anika)                        │
│    ┌────────────────────────────────────┐               │
│    │ • PID namespace                    │               │
│    │ • UTS namespace                    │               │
│    │ • Mount namespace                  │               │
│    │ • seccomp filters                  │               │
│    │ • Drop privileges                  │               │
│    └────────┬───────────────────────────┘               │
└─────────────┼────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│           Application Execution                         │
│              (calc, test, etc.)                         │
└─────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│          Output Returned to User                        │
└─────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Setup (WSL)

### 1. Run Setup Script

```bash
cd /mnt/c/Users/Dell/Documents/GitHub/SafeBox_
./setup_wsl.sh
```

This installs:
- Build tools (gcc, g++, cmake)
- libseccomp (for sandboxing)
- Python packages (Flask, Rich, FastAPI, etc.)
- Builds all components

### 2. Verify Build

```bash
ls -la src/safebox           # Sandbox binary
ls -la build/safebox_cgroup  # cgroup agent
ls -la src/calc_with_selftest # Test app
ls -la src/test              # Test app
```

### 3. Run Real System

```bash
sudo python3 cli/real_safebox_cli.py
```

---

## Usage Example

### Terminal Session

```
$ sudo python3 cli/real_safebox_cli.py

╔═══════════════════════════════════════════════════════════╗
║   🔒 SafeBox - Real System Resource Manager 🔒           ║
║   Banker's Algorithm → cgroups → Sandbox → Safe Execution ║
╚═══════════════════════════════════════════════════════════╝

Checking Prerequisites...
✅ All prerequisites met

✅ System Ready!
   Total Resources: CPU=100%, Memory=1024MB

📊 System Status
┌─────────────────┬────────────────────────┐
│ System State    │ ✅ SAFE                │
│ Active Jobs     │ 0                      │
│ CPU Available   │ 100%                   │
│ Memory Available│ 1024MB                 │
└─────────────────┴────────────────────────┘

═══════ Main Menu ═══════
1. 📊 Show System State
2. 🚀 Run New Job
3. 📱 List Available Apps
4. 🔄 Refresh
5. 🚪 Exit

Select option: 2

═══ Run New Job ═══

📱 Available Applications
┌───┬──────────────────────┬────────────┬──────┬────────┐
│ # │ Name                 │ Path       │ CPU% │ Memory │
├───┼──────────────────────┼────────────┼──────┼────────┤
│ 1 │ Calculator Self-Test │ src/calc.. │ 20   │ 50MB   │
│ 2 │ Test Program         │ src/test   │ 10   │ 30MB   │
└───┴──────────────────────┴────────────┴──────┴────────┘

Select application number: 1
Enter job name: Math Calculation
CPU limit (1-100%): 20
Memory limit (MB): 50
Application arguments (optional): 

📋 Job Summary:
   Name: Math Calculation
   App: Calculator Self-Test
   Path: /path/to/calc_with_selftest
   CPU: 20%
   Memory: 50MB

Submit job? [Y/n]: y

⏳ Submitting job...

✅ Created cgroup: safebox_job_1
✅ Applied CPU limit: 20%
✅ Applied memory limit: 50MB
🚀 Launching: /path/to/safebox /path/to/calc_with_selftest
✅ Execution completed

┌─────────────────── ✅ Job Completed ───────────────────┐
│ ✅ SUCCESS: System remains in SAFE state              │
│ Safe Sequence: Math Calculation →                     │
│                                                        │
│ 📊 Output:                                            │
│ Self-test passed!                                     │
│ Calculator ready.                                     │
│ 5 + 3 = 8                                            │
│ 10 - 2 = 8                                           │
└────────────────────────────────────────────────────────┘

Release resources now? [Y/n]: y
✅ Released job 1: Resources released successfully
```

---

## What Happens Behind the Scenes

### 1. **Banker's Algorithm Check** (Ritika's Code)
```python
# In backend/app/system_executor.py
success, msg = self.banker.request_resources(job_id, [cpu%, memory_mb])
if not success:
    return False, "🚫 UNSAFE - Request REJECTED"
```

### 2. **cgroup Creation** (Ayush's Code)
```bash
# Calls C++ cgroup agent
./build/safebox_cgroup create safebox_job_1
./build/safebox_cgroup cpu.set safebox_job_1 20000 100000
./build/safebox_cgroup mem.set safebox_job_1 52428800
```

### 3. **Sandbox Execution** (Anika's Code)
```bash
# Calls SafeBox sandbox
./src/safebox /path/to/calc_with_selftest
# Inside safebox:
# - Creates namespaces (PID, UTS, Mount)
# - Applies seccomp filters
# - Drops privileges
# - Executes app safely
```

---

## Testing Different Scenarios

### Scenario 1: Safe Request
```
Job 1: CPU=20%, Memory=50MB  → ✅ GRANTED
Job 2: CPU=30%, Memory=100MB → ✅ GRANTED
Job 3: CPU=40%, Memory=200MB → ✅ GRANTED
System: SAFE (sequence exists)
```

### Scenario 2: Unsafe Request (Rejected)
```
Job 1: CPU=60%, Memory=500MB → ✅ GRANTED
Job 2: CPU=50%, Memory=600MB → 🚫 REJECTED
Reason: Would exceed available resources
System: Remains SAFE
```

### Scenario 3: Resource Limits Enforced
```
Job: CPU=20%, Memory=50MB
Try to use 30% CPU → ⚠️ cgroup throttles to 20%
Try to use 100MB RAM → ⚠️ cgroup limits to 50MB
```

---

## Team Contributions

### Ritika - Banker's Algorithm
**File:** `backend/app/banker.py`
- Deadlock prevention algorithm
- Safety checking
- Resource allocation/release
- Safe sequence computation

### Ayush - cgroup Management
**File:** `cgroup_agent/src/cgroups.cpp`
- cgroup v2 creation
- CPU quota/period limits
- Memory limits
- Process attachment

### Anika - Sandbox Security
**File:** `src/safebox.c`
- Namespace isolation (PID, UTS, Mount)
- seccomp syscall filtering
- Privilege dropping
- Secure execution environment

---

## Troubleshooting

### Error: "Must run as root"
```bash
sudo python3 cli/real_safebox_cli.py
```

### Error: "SafeBox binary not found"
```bash
make build-c
```

### Error: "cgroup agent not found"
```bash
make build-cpp
```

### Error: "cgroup v2 not available"
Check WSL kernel:
```bash
cat /proc/cgroups
ls /sys/fs/cgroup/cgroup.controllers
```

---

## Comparison: Real vs Simulation

| Feature | Simulation Mode | Real System Mode |
|---------|----------------|------------------|
| Banker's Algorithm | ✅ Working | ✅ Working |
| Resource Limits | ❌ Fake | ✅ Real (cgroups) |
| Sandboxing | ❌ None | ✅ Namespaces + seccomp |
| Application Execution | ❌ Mock | ✅ Real binaries |
| Safety Enforcement | ✅ Algorithm only | ✅ Algorithm + OS |
| Requires Root | ❌ No | ✅ Yes |
| Works on Windows | ✅ Yes | ❌ Linux/WSL only |

---

## For Mentor Demonstration

**Show Real System Flow:**

1. **Start CLI:** `sudo python3 cli/real_safebox_cli.py`
2. **Show system state:** Option 1
3. **Run safe job:** Option 2, select app, enter limits
4. **Show Banker's approval:** See "✅ SAFE" message
5. **See real execution:** Application output shown
6. **Run unsafe job:** Try requesting 200% CPU
7. **Show rejection:** Banker's Algorithm rejects
8. **System stays safe:** No deadlock possible

**Key Points to Emphasize:**
- ✅ Real Banker's Algorithm (not just demo)
- ✅ Real cgroups (actual OS resource limits)
- ✅ Real sandbox (kernel namespaces + seccomp)
- ✅ All three team members' work integrated
- ✅ Production-ready architecture

---

## Next Steps

1. **Add more test applications**
2. **Web UI integration** with real system
3. **Performance monitoring** dashboard
4. **Multi-user support**
5. **Docker/container integration**

🎉 **SafeBox is now a REAL system!** 🎉
