# SafeBox - Mentor Presentation Guide

## 🎯 **Objective: Show ONE INTEGRATED SYSTEM (Not 3 Separate Projects)**

---

## 📋 **Pre-Presentation Checklist**

```bash
# 1. Ensure dependencies are installed
make install-deps

# 2. Test the integrated demo
python3 integrated_demo.py 4

# 3. Have terminals ready
Terminal 1: For running demos
Terminal 2: For showing code
Terminal 3: Optional - for backend/web UI
```

---

## 🎬 **Presentation Flow (15-20 minutes)**

### **Part 1: Introduction (2 min)**

**Say:**
> "We've built SafeBox - an integrated secure execution environment that combines three major OS concepts:
> - **Ritika**: Resource management with Banker's Algorithm  
> - **Ayush**: Real-time performance monitoring with cgroups
> - **Anika**: Security isolation with namespaces and seccomp
> 
> The key point: **This is ONE integrated system** where every request flows through all three components."

---

### **Part 2: Architecture Overview (3 min)**

**Show: `INTEGRATED_DEMO.md`**

**Explain the flow:**
```
User Request
    ↓
[RITIKA] Banker's Algorithm → Checks if safe (deadlock prevention)
    ↓ (If approved)
[AYUSH] cgroups Monitoring → Sets resource limits & tracks usage
    ↓ (Resources allocated)
[ANIKA] Security Sandbox → Executes in isolated environment
    ↓
Safe Execution Complete
```

**Say:**
> "Notice how data flows through ALL three layers for EVERY request. This isn't three separate demos - it's one integrated pipeline."

---

### **Part 3: Live Demo - Scenario 1: Normal Flow (4 min)**

**Run:**
```bash
python3 integrated_demo.py 1
```

**Point out:**
1. ✅ **[RITIKA]** - Banker approves the request (shows safe sequence)
2. ✅ **[AYUSH]** - cgroups configured with CPU/memory limits
3. ✅ **[ANIKA]** - Process executes in sandbox
4. ✅ **[INTEGRATED]** - All three report success together

**Say:**
> "See how EVERY execution goes through all three team members' code. Ritika's algorithm gates the request, Ayush's monitoring tracks it, and Anika's sandbox secures it."

---

### **Part 4: Live Demo - Scenario 2: Deadlock Prevention (4 min)**

**Run:**
```bash
python3 integrated_demo.py 2
```

**Point out:**
- ❌ **[RITIKA]** - Banker REJECTS unsafe request
- The request never reaches Ayush or Anika
- System stays safe - no deadlock possible

**Say:**
> "This demonstrates the integration: Ritika's layer protects the entire system. If her algorithm rejects it, nothing else runs. This is real integration, not just calling separate functions."

---

### **Part 5: Live Demo - Scenario 3: Security Block (3 min)**

**Run:**
```bash
python3 integrated_demo.py 3
```

**Point out:**
- ✅ **[RITIKA]** - Banker approves (resources are fine)
- ✅ **[AYUSH]** - cgroups set up monitoring
- 🛑 **[ANIKA]** - seccomp BLOCKS malicious syscall

**Say:**
> "Even if a request passes resource checks, Anika's security layer can still block it. All three layers work together to ensure safe execution."

---

### **Part 6: Code Integration Points (4 min)**

**Show: `integrated_demo.py` (lines 90-180)**

**Highlight:**

```python
# This function shows REAL integration
def execute_integrated_request(...):
    # Phase 1: RITIKA checks with Banker
    success, message = self.banker.request_resources(pid, request)
    if not success:
        return False  # Rejected - deadlock prevention
    
    # Phase 2: AYUSH sets up monitoring
    cpu_limit = sum(process.allocated) * 10
    self.cgroups_active[pid] = {...}
    
    # Phase 3: ANIKA executes in sandbox
    # Uses cgroup from Ayush, allocation from Ritika
    sandbox.execute(code)
```

**Say:**
> "This is actual integrated code. Each phase uses data from the previous phase. The cgroup limits come from Ritika's allocation. The sandbox uses Ayush's monitoring path. Everything is connected."

---

### **Part 7: Show Code from Each Team Member (Optional - if time)**

**RITIKA's Code:** `backend/app/banker.py`
```python
def request_resources(self, pid: int, request: List[int]):
    # Safety algorithm implementation
    is_safe, safe_sequence = self.is_safe_state()
    # This gates ALL requests in the system
```

**AYUSH's Code:** `backend/app/cgroups_client.py`
```python
def set_limits(self, cpu, memory):
    # cgroups configuration
    # Monitors ALL approved processes
```

**ANIKA's Code:** `src/namespaces.c` and `src/seccomp_policy.c`
```c
// Creates isolated execution environment
// Protects ALL running processes
```

---

## 🎤 **Key Points to Emphasize**

### ✅ **What Makes This Integrated:**

1. **Shared Data Structures**
   - Banker's allocation → used by cgroups limits
   - cgroup paths → used by sandbox
   - Security events → logged in metrics

2. **Sequential Flow**
   - EVERY request goes through ALL three layers
   - Can't skip any layer
   - Rejection at any layer stops the flow

3. **Unified API**
   - Single backend endpoint calls all three
   - Web UI shows all three status together
   - Logs include all three components

4. **Real Dependencies**
   - Ayush needs Ritika's allocation to set limits
   - Anika needs Ayush's cgroup path for isolation
   - Metrics combine data from all three

---

## 📊 **Optional: Web UI Demo (if time)**

```bash
# Start integrated backend + web UI
make start-integrated

# Open: http://localhost:5001
```

**Show in UI:**
- Dashboard displays ALL THREE components
- Resource allocation (Ritika)
- Live monitoring (Ayush)
- Security status (Anika)

---

## 💡 **Anticipated Questions & Answers**

### **Q: "How is this different from three separate projects?"**
**A:** "Every execution flows through ALL three layers. The data from one layer is used by the next. We have integration tests that verify all three work together. We can't demo one without the others."

### **Q: "Can you show me where the integration happens?"**
**A:** "`integrated_demo.py` and `backend/app/main.py` - these files call all three subsystems for every request. Also, `Makefile` has `integrated-demo` target that runs the complete system."

### **Q: "What if one component fails?"**
**A:** "The whole request fails gracefully. For example, if Ritika's Banker rejects, Ayush and Anika never run. If Anika's security blocks something, it reports back through the integrated pipeline."

---

## 📝 **Closing Statement**

**Say:**
> "To summarize: SafeBox is ONE integrated system where:
> - Ritika's Banker Algorithm provides intelligent resource management
> - Ayush's cgroups monitoring tracks every execution
> - Anika's security sandbox protects every process
> 
> Every feature demonstrates all three components working together. This is real systems integration, not just three independent modules."

---

## 🚀 **Quick Command Reference**

```bash
# Complete integrated demo (BEST for mentor)
python3 integrated_demo.py complete

# All scenarios interactively
python3 integrated_demo.py

# Individual scenarios
python3 integrated_demo.py 1  # Normal flow
python3 integrated_demo.py 2  # Deadlock prevention  
python3 integrated_demo.py 3  # Security enforcement
python3 integrated_demo.py 4  # Complete workflow

# Web interface
make start-integrated
# Then open: http://localhost:5001

# Run tests showing integration
make test-integration
```

---

## ✅ **Success Indicators**

**Your mentor should see:**
- [ ] ONE execution flow through three layers
- [ ] Shared data between components
- [ ] Integration code (not just separate function calls)
- [ ] Unified error handling
- [ ] Combined status reporting
- [ ] Real dependencies between layers

**If they still think it's separate, show:**
- `integrated_demo.py` - single script using ALL three
- API calls that touch ALL components
- Makefile targets for integrated testing
- Dashboard showing unified state

---

## 🎯 **Bottom Line**

**This is ONE SYSTEM with three integrated components, not three projects running side-by-side!**

Good luck with your presentation! 🚀
