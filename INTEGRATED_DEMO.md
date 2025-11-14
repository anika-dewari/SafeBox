# SafeBox - Integrated System Demonstration

## 🎯 Complete Integration Architecture

### Team Members & Integration Points:

**Anika (Security Layer)** → **Ayush (Monitoring)** → **Ritika (Resource Management)**

```
┌─────────────────────────────────────────────────────────────────┐
│                     SAFEBOX INTEGRATED SYSTEM                    │
└─────────────────────────────────────────────────────────────────┘

    USER REQUEST
        ↓
┌───────────────────┐
│  RITIKA'S LAYER   │  ← Banker's Algorithm decides if request is safe
│  Banker Algorithm │  ← CLI/Web UI for user interaction
│  (Resource Mgmt)  │  ← Deadlock prevention logic
└─────────┬─────────┘
          ↓ [Request Approved]
┌───────────────────┐
│   AYUSH'S LAYER   │  ← cgroups monitoring active
│  cgroups Agent    │  ← Real-time resource tracking
│  Performance Mon  │  ← Metrics collection
└─────────┬─────────┘
          ↓ [Resources Allocated]
┌───────────────────┐
│   ANIKA'S LAYER   │  ← Process launched in sandbox
│   Namespaces      │  ← Security isolation applied
│   seccomp         │  ← System calls restricted
│   SafeBox Core    │  ← Execution monitored
└───────────────────┘
          ↓
    SAFE EXECUTION
```

---

## 🔗 Integration Flow

### Phase 1: Request Validation (Ritika)
1. User requests to run code with resource requirements
2. **Banker's Algorithm** checks if allocation is safe
3. If safe → proceed; If unsafe → reject (deadlock prevention)

### Phase 2: Resource Allocation (Ayush)
4. **cgroups** are configured with approved limits
5. **Monitoring agent** starts tracking
6. **Metrics collection** begins

### Phase 3: Secure Execution (Anika)
7. **Namespace isolation** created
8. **seccomp policy** applied
9. **Process executes** in sandbox
10. **Security enforced** throughout execution

### Phase 4: Monitoring & Cleanup (All Integrated)
11. **Ayush's agent** reports resource usage
12. **Ritika's algorithm** updates available resources
13. **Anika's sandbox** terminates safely

---

## 📊 Data Flow Between Components

```python
# RITIKA → AYUSH → ANIKA Integration

# 1. Ritika's Banker approves allocation
allocation = banker.request_resources(process_id, [2, 1, 0])
if allocation['safe']:
    
    # 2. Ayush's cgroups sets limits
    cgroups.set_limits(
        cpu_shares=allocation['cpu'],
        memory_limit=allocation['memory']
    )
    
    # 3. Anika's sandbox executes
    sandbox = SafeBox(
        namespaces=['pid', 'net', 'mnt'],
        cgroup_path=cgroups.path,
        seccomp_policy='strict'
    )
    sandbox.execute(user_code)
```

---

## 🎬 Live Demo Script

### Step 1: Initialize Integrated System
```bash
# Start all components together
make integrated-demo
```

### Step 2: Show Resource Request Flow
```bash
# User submits job through Ritika's UI
# → Banker checks safety
# → Ayush configures cgroups  
# → Anika executes in sandbox
python3 integrated_demo.py --scenario safe_allocation
```

### Step 3: Show Deadlock Prevention
```bash
# Request that would cause deadlock
# → Ritika's Banker REJECTS
# → System stays safe
python3 integrated_demo.py --scenario unsafe_request
```

### Step 4: Show Security Enforcement
```bash
# Malicious code attempt
# → Passes Banker (resources OK)
# → Passes cgroups (limits set)
# → BLOCKED by Anika's seccomp
python3 integrated_demo.py --scenario security_test
```

---

## 🔧 Integration Points in Code

### 1. Backend API Integration (`backend/app/main.py`)
```python
@app.post("/execute")
async def execute_code(request: ExecutionRequest):
    # RITIKA: Check with Banker
    safe = banker.request_resources(request.process_id, request.resources)
    if not safe:
        return {"status": "rejected", "reason": "deadlock prevention"}
    
    # AYUSH: Configure monitoring
    cgroup_id = cgroups.create(request.limits)
    metrics.start_monitoring(cgroup_id)
    
    # ANIKA: Execute in sandbox
    result = safebox.execute(
        code=request.code,
        cgroup=cgroup_id,
        timeout=request.timeout
    )
    
    # Return integrated result
    return {
        "banker_decision": safe,
        "resource_usage": metrics.get_stats(cgroup_id),
        "execution_result": result,
        "security_events": safebox.get_violations()
    }
```

### 2. CLI Integration (`cli/safebox_cli.py`)
```python
def run_integrated(args):
    print("🔗 SafeBox Integrated Execution")
    print("=" * 60)
    
    # Show all three layers working
    print("\n[RITIKA] Banker's Algorithm checking...")
    print("[AYUSH] Setting up cgroups monitoring...")
    print("[ANIKA] Configuring security sandbox...")
    
    result = execute_integrated(args.code, args.resources)
    
    print(f"\n✅ Banker Status: {result.banker}")
    print(f"📊 Resource Usage: {result.metrics}")
    print(f"🔒 Security Status: {result.security}")
```

---

## 📈 Metrics Dashboard Integration

The web UI shows all three components in real-time:

```
┌─────────────────────────────────────────────────────────┐
│              SafeBox Integrated Dashboard                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [RITIKA] Banker's Algorithm Status                     │
│  ├─ Available Resources: [3, 2, 1]                     │
│  ├─ Active Processes: 4                                │
│  └─ Safe Sequence: P0 → P2 → P3 → P1                  │
│                                                          │
│  [AYUSH] Resource Monitoring                            │
│  ├─ CPU Usage: 45%  [████████░░░░░░░░]                │
│  ├─ Memory: 2.1GB / 4GB  [█████████████░░░░]          │
│  └─ cgroups Active: 4                                  │
│                                                          │
│  [ANIKA] Security Status                                │
│  ├─ Active Sandboxes: 4                                │
│  ├─ Blocked Syscalls: 23                               │
│  └─ Security Violations: 0 ✅                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎓 Mentor Presentation Points

### "This is ONE INTEGRATED SYSTEM where:"

1. **User Input** → Goes through ALL three layers
2. **Ritika's Algorithm** → Gates all resource requests
3. **Ayush's Monitoring** → Tracks all executions
4. **Anika's Security** → Protects all processes
5. **Data Flows** → Between all components
6. **Single Dashboard** → Shows all three working together

### Key Integration Features:
✅ Shared data structures between components
✅ API calls flow through all layers
✅ Real-time coordination
✅ Unified error handling
✅ Combined metrics and logging

---

## 🚀 Quick Start for Demo

```bash
# 1. Build all components
make all

# 2. Start integrated system
./scripts/run_integrated.sh

# 3. Access unified dashboard
open http://localhost:5001

# 4. Run test scenarios showing integration
python3 tests/test_integration.py
```

---

## 📝 Test Cases Showing Integration

1. **Normal Flow**: Request → Banker → cgroups → Sandbox → Success
2. **Deadlock Prevention**: Request → Banker BLOCKS → No execution
3. **Resource Limit**: Request → Approved → cgroups LIMITS → Execution throttled
4. **Security Block**: Request → Approved → Limits Set → seccomp BLOCKS malicious call

All three team members' work is visible in EACH test case!
