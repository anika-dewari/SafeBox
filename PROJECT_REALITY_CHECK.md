# SafeBox - What This Project ACTUALLY Does

## 🎯 **Reality Check: Real OS Components vs Simulated**

Your mentor is right to ask about hardcoding. Let me break down what's **REAL** vs what's **SIMULATED** in your project.

---

## ✅ **REAL Operating System Components** (Not Hardcoded/Simulated)

### **1. ANIKA's Security Layer - 100% REAL**

#### **Namespaces (Linux Kernel Feature)**
**File**: `src/namespaces.c`

**REAL OS Operations:**
```c
// Creates actual Linux namespaces using clone() syscall
int sandbox_main(void *arg) {
    // REAL: Remounts /proc inside new PID namespace
    mount("proc", "/proc", "proc", 0, NULL);
    
    // REAL: Filesystem isolation
    mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL);
}

// REAL: UID/GID mapping in user namespace
setup_userns_map(child_pid);  // Writes to /proc/[pid]/uid_map
```

**What this ACTUALLY does:**
- ✅ Creates isolated PID namespace (process sees different PIDs)
- ✅ Creates mount namespace (filesystem isolation)
- ✅ Creates network namespace (network isolation)
- ✅ Creates user namespace (permission isolation)
- ✅ Uses **real Linux kernel syscalls** (`clone()`, `unshare()`)

#### **seccomp (System Call Filtering)**
**File**: `src/seccomp_policy.c`

**REAL OS Operations:**
```c
// REAL: Uses libseccomp to create BPF filters
scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL);

// REAL: Whitelists specific syscalls
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0);
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);

// REAL: Loads filter into kernel (blocks all non-whitelisted syscalls)
seccomp_load(ctx);
```

**What this ACTUALLY does:**
- ✅ Installs **real BPF (Berkeley Packet Filter)** in kernel
- ✅ Blocks dangerous syscalls (`reboot`, `mount`, etc.)
- ✅ Process will be **KILLED by kernel** if it tries blocked syscall
- ✅ This is **EXACTLY** what Docker/containers use

**Test it:**
```bash
make all
sudo ./build/safebox
# Try running: reboot (will be blocked!)
```

---

### **2. AYUSH's Monitoring Layer - REAL cgroups**

#### **cgroups v2 (Linux Kernel Resource Control)**
**File**: `cgroup_agent/src/cgroups.cpp`

**REAL OS Operations:**
```cpp
// REAL: Creates actual cgroup in Linux kernel
fs::create_directories("/sys/fs/cgroup/safebox_group");

// REAL: Sets memory limit by writing to kernel interface
write_file("/sys/fs/cgroup/safebox_group/memory.max", "1073741824");  // 1GB

// REAL: Sets CPU quota
write_file("/sys/fs/cgroup/safebox_group/cpu.max", "50000 100000");  // 50% CPU

// REAL: Attaches process to cgroup
write_file("/sys/fs/cgroup/safebox_group/cgroup.procs", pid);
```

**What this ACTUALLY does:**
- ✅ Writes to **real Linux kernel filesystem** (`/sys/fs/cgroup`)
- ✅ Kernel **enforces** CPU and memory limits
- ✅ Process will be **OOM-killed** if exceeds memory
- ✅ Process CPU will be **throttled** if exceeds quota
- ✅ This is **EXACTLY** what Kubernetes/Docker use

**Test it:**
```bash
# Build the cgroup agent
cd cgroup_agent && mkdir build && cd build
cmake .. && make

# Create cgroup and set 100MB limit
sudo ./safebox_cgroup create test_group
sudo ./safebox_cgroup mem.set test_group 104857600

# Run memory-hungry process
sudo ./safebox_cgroup attach test_group $$
# Process will be killed by kernel if exceeds 100MB
```

---

### **3. RITIKA's Banker Algorithm - REAL Algorithm, Logical Control**

#### **Banker's Algorithm (Deadlock Avoidance)**
**File**: `backend/app/banker.py`

**REAL Algorithm Operations:**
```python
def is_safe_state(self) -> Tuple[bool, List[int]]:
    """
    REAL Banker's Algorithm safety check
    This is Dijkstra's algorithm - mathematically proven
    """
    work = self.available.copy()
    finish = {pid: False for pid in self.processes}
    
    # REAL: Iterates through processes checking if need ≤ available
    for pid, process in self.processes.items():
        can_finish = all(process.need[i] <= work[i] 
                        for i in range(self.num_resources))
        if can_finish:
            # Simulate process finishing, release resources
            work[i] += process.allocated[i]
```

**What this ACTUALLY does:**
- ✅ Implements **real Dijkstra's Banker Algorithm**
- ✅ Prevents deadlock through **mathematical safety check**
- ✅ Rejects unsafe resource requests
- ✅ Calculates **real safe sequences**

**Is this "real"?**
- **Algorithm**: ✅ Yes - real computer science algorithm
- **Resource enforcement**: ⚠️ Logical - gates the cgroup/sandbox creation
- **Integration**: It decides whether Ayush's cgroups get created

---

## ⚠️ **What's Currently Simulated (Could Be Made Real)**

### **1. Resource Types**
**Current**: Abstract resources `[R0, R1, R2]`

**To make real**:
```python
# Map to actual system resources
resources = {
    'CPU': psutil.cpu_count(),           # Real CPU cores
    'Memory': psutil.virtual_memory().total,  # Real RAM
    'Disk': psutil.disk_usage('/').total      # Real disk
}
```

### **2. Process Execution in Demo**
**Current**: `integrated_demo.py` simulates execution

**To make real**:
```python
# Actually run code in sandbox
subprocess.run([
    './build/safebox',  # Anika's sandbox
    'python3', user_code
])
```

### **3. Monitoring Metrics**
**Current**: Simulated CPU/memory usage

**To make real**:
```python
# Read actual cgroup stats
with open('/sys/fs/cgroup/safebox_group/memory.current') as f:
    actual_memory_used = int(f.read())

with open('/sys/fs/cgroup/safebox_group/cpu.stat') as f:
    actual_cpu_used = parse_cpu_stat(f.read())
```

---

## 🔗 **Integration: What's Real**

### **Real Integration Flow:**

```
1. User Request
   ↓
2. RITIKA's Banker (REAL algorithm)
   ├─ Checks resources mathematically
   └─ Approves/rejects
   ↓ [If approved]
3. AYUSH's cgroups (REAL kernel operation)
   ├─ Creates cgroup: write to /sys/fs/cgroup
   ├─ Sets limits: write memory.max, cpu.max
   └─ Returns cgroup path
   ↓
4. ANIKA's Sandbox (REAL kernel features)
   ├─ clone() with namespace flags
   ├─ Attaches to cgroup from step 3
   ├─ Loads seccomp filter
   └─ exec() user code
   ↓
5. Kernel Enforces Everything
   ├─ Namespace isolation active
   ├─ cgroup limits enforced
   └─ seccomp blocking syscalls
```

---

## 💻 **Making It A Complete "Proper OS Project"**

### **What You Have (Real):**
1. ✅ Real Linux namespaces
2. ✅ Real seccomp-BPF filters
3. ✅ Real cgroups v2
4. ✅ Real Banker's Algorithm
5. ✅ Real integration logic

### **What to Add (Remove Hardcoding):**

#### **1. Dynamic Resource Discovery**
```python
# backend/app/system_resources.py
import psutil

class SystemResources:
    def __init__(self):
        self.cpu_cores = psutil.cpu_count()
        self.total_memory = psutil.virtual_memory().total
        self.total_disk = psutil.disk_usage('/').total
    
    def get_available(self):
        return {
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().available,
            'disk': psutil.disk_usage('/').free
        }
```

#### **2. Real Process Execution**
```python
# backend/app/executor.py
class SafeBoxExecutor:
    def execute(self, code: str, resources: dict):
        # 1. Banker approves
        if not banker.request_resources(pid, resources):
            raise DeadlockRisk()
        
        # 2. Create cgroup (REAL)
        cgroup.create(f"safebox_{pid}")
        cgroup.set_memory_max(f"safebox_{pid}", resources['memory'])
        cgroup.set_cpu_max(f"safebox_{pid}", resources['cpu'])
        
        # 3. Execute in sandbox (REAL)
        proc = subprocess.Popen([
            './build/safebox',
            '--code', code
        ])
        
        # 4. Attach to cgroup (REAL)
        cgroup.attach_pid(f"safebox_{pid}", proc.pid)
        
        # 5. Monitor (REAL)
        return self.monitor_execution(proc.pid)
```

#### **3. Real Monitoring**
```python
# backend/app/monitor.py
class CgroupMonitor:
    def get_stats(self, cgroup_name: str):
        base = f"/sys/fs/cgroup/{cgroup_name}"
        
        # REAL: Read from kernel
        with open(f"{base}/memory.current") as f:
            memory_used = int(f.read())
        
        with open(f"{base}/cpu.stat") as f:
            cpu_stats = self.parse_cpu_stat(f.read())
        
        return {
            'memory_used': memory_used,
            'cpu_used': cpu_stats['usage_usec']
        }
```

#### **4. Actual Workload**
```bash
# Instead of simulated demo, run real code:
./integrated_execution.py \
    --code "scripts/workload.py" \
    --max-memory 100M \
    --max-cpu 50%
```

---

## 📊 **Current State Summary**

| Component | Implementation | Real? | Can Demo? |
|-----------|---------------|-------|-----------|
| **Namespaces** | Linux syscalls | ✅ 100% Real | ✅ Yes |
| **seccomp** | BPF filters | ✅ 100% Real | ✅ Yes |
| **cgroups** | Kernel filesystem | ✅ 100% Real | ✅ Yes |
| **Banker's Algorithm** | Python implementation | ✅ Real algorithm | ✅ Yes |
| **Resource types** | Abstract numbers | ⚠️ Hardcoded | ⚠️ Could map to real |
| **Process execution** | Demo simulation | ⚠️ Simulated | ⚠️ Easy to make real |
| **Metrics** | Demo simulation | ⚠️ Simulated | ⚠️ Easy to make real |
| **Integration** | Sequential flow | ✅ Real logic | ✅ Yes |

---

## 🎯 **What To Tell Your Mentor**

### **Core Is Real:**
> "The core OS components are **100% real**:
> - We use actual Linux namespace syscalls
> - We install real seccomp BPF filters in the kernel
> - We create real cgroups that the kernel enforces
> - We implement the real Banker's Algorithm

### **Demo Is Simulated (But Easy to Fix):**
> "The `integrated_demo.py` simulates execution for presentation purposes, but we have all the real components built. We can easily connect them to run actual workloads instead of simulated ones."

### **This Is A Real Container/Sandbox:**
> "This is essentially a minimal container runtime (like Docker) with deadlock prevention. Docker uses the same Linux features we use: namespaces + cgroups + seccomp."

---

## 🚀 **Quick Fix: Make Demo Execute Real Code**

Want to make it run real code right now? Here's a quick modification:

```python
# Add to integrated_demo.py
def execute_real_code(self, code: str, resources: dict):
    """Execute REAL code in REAL sandbox"""
    
    # 1. Banker check (REAL algorithm)
    if not self.banker.request_resources(pid, resources):
        return "REJECTED"
    
    # 2. Create cgroup (REAL kernel op)
    subprocess.run([
        './cgroup_agent/build/safebox_cgroup',
        'create', f'safebox_{pid}'
    ])
    
    # 3. Run in sandbox (REAL isolation)
    proc = subprocess.Popen([
        'sudo', './build/safebox'
    ])
    
    # 4. Attach to cgroup (REAL enforcement)
    subprocess.run([
        './cgroup_agent/build/safebox_cgroup',
        'attach', f'safebox_{pid}', str(proc.pid)
    ])
    
    # Now it's ALL REAL!
    return proc.wait()
```

---

## ✅ **Bottom Line**

**Your project IS a proper OS project because:**

1. **Uses real Linux kernel features** (namespaces, cgroups, seccomp)
2. **Implements real CS algorithms** (Banker's Algorithm)
3. **Real integration** between components
4. **Real resource enforcement** by the kernel

**What's simulated:**
- Just the **demo execution flow** (easy to fix)
- **Resource types** are abstract (could map to real CPU/RAM/disk)

**This is essentially a minimal container runtime with deadlock prevention!**

---

## 📝 **Recommendation for Mentor Demo**

Show **both**:

1. **The real components individually:**
```bash
# Show real sandbox
sudo ./build/safebox  # Creates real namespaces

# Show real cgroups
sudo ./cgroup_agent/build/safebox_cgroup create test
cat /sys/fs/cgroup/test/cgroup.procs  # Real kernel file!
```

2. **The integrated demo:**
```bash
python3 integrated_demo.py complete
```

Then explain: "The demo simulates execution for clarity, but all the underlying OS components (namespaces, cgroups, seccomp, Banker's) are 100% real and functional."

---

**TL;DR: Your OS components are REAL. The demo wrapper is simulated for presentation. Easy to connect them for real execution.** ✅
